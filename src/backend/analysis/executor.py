# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Module that owns the process pool in which the analysis business logic is
executed.
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Self

from backend.analysis.errors import AnalysisBusyError
from backend.analysis.schemas import (
    AnalysisResult,
    BarrierDescription,
    OperatorDescription,
    OperatorRequest,
    OperatorResult,
)
from backend.analysis.worker import (
    analyze_text,
    get_barrier_definitions,
    get_operator_descriptions,
    get_operators,
)
from backend.parlance.schemas import ParlanceWord


class AnalysisExecutor:
    """
    Executor for handing off analysis jobs to available analysis workers..

    Parameters
    ----------
    pool : ProcessPoolExecutor
        The pool of processes that perform the actual operation. Please note
        that each pool loads its own instance of a (large-ish) spaCy model, so
        increasing this comes with RAM cost. Also keep in mind that each fastAPI
        worker has its own pool, so the number of models loaded is "number of
        fastAPI workers x number of pool workers".
    barrier_definitions: list[BarrierDescription]
        A list of BarrierDescription objects for the types of barriers that the
        analyzer behind the executor supports.
    max_outstanding : int = 2
        The number of pending analysis requests that are held before the worker
        starts rejecting new ones outright.
    """

    def __init__(
        self,
        pool: ProcessPoolExecutor,
        barrier_definitions: list[BarrierDescription],
        operator_descriptions: list[OperatorDescription],
        *,
        max_outstanding: int = 2,
    ) -> None:
        if max_outstanding < 1:
            raise ValueError("max_outstanding must be at least 1")

        self._pool = pool
        self._max_outstanding = max_outstanding
        self._pending: set[asyncio.Future[AnalysisResult]] = set()
        self._barrier_definitions = tuple(
            definition.model_copy(deep=True)
            for definition in barrier_definitions
        )
        self._operator_descriptions: list[OperatorDescription] = [
            description.model_copy(deep=True)
            for description in operator_descriptions
        ]

    @classmethod
    async def create(
        cls,
        pool: ProcessPoolExecutor,
        *,
        max_outstanding: int = 2,
    ) -> Self:
        """
        Factory for an AnalysisExecutor whose barrier definitions are fetched
        from a pool worker. This way, an executor can be created without the
        need for the creating function to know domain-specific details.
        """
        loop = asyncio.get_running_loop()
        barriers = await loop.run_in_executor(pool, get_barrier_definitions)
        operators = await loop.run_in_executor(pool, get_operator_descriptions)
        return cls(pool, barriers, operators, max_outstanding=max_outstanding)

    async def analyze(
        self,
        text: str,
        parlance_words: list[ParlanceWord] | None = None,
        check_barriers: bool = True,
    ) -> AnalysisResult:
        """Submit analysis without blocking the API event loop."""
        if len(self._pending) >= self._max_outstanding:
            raise AnalysisBusyError("Analysis capacity is exhausted")

        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(
            self._pool, analyze_text, text, parlance_words, check_barriers
        )

        self._pending.add(future)
        future.add_done_callback(self._on_done)

        # Request cancellation must not release capacity while the
        # subprocess is still executing the analysis.
        return await asyncio.shield(future)

    def get_barrier_definitions(self) -> list[BarrierDescription]:
        """Return cached metadata without occupying an analysis worker."""
        return [
            definition.model_copy(deep=True)
            for definition in self._barrier_definitions
        ]

    async def get_operators(
        self, operator_request: OperatorRequest
    ) -> OperatorResult:
        """Return operators found in a string"""
        if len(self._pending) >= self._max_outstanding:
            raise AnalysisBusyError("Analysis capacity is exhausted")

        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(
            self._pool, get_operators, operator_request
        )

        self._pending.add(future)
        future.add_done_callback(self._on_done)

        # Request cancellation must not release capacity while the
        # subprocess is still executing the analysis.
        return await asyncio.shield(future)

    def get_operator_descriptions(self) -> list[OperatorDescription]:
        return [
            operator.model_copy(deep=True)
            for operator in self._operator_descriptions
        ]

    def _on_done(
        self,
        future: asyncio.Future[AnalysisResult],
    ) -> None:
        self._pending.discard(future)

        # Retrieve exceptions even if the requesting task was cancelled.
        # A caller still awaiting the future receives the exception normally.
        if not future.cancelled():
            _ = future.exception()
