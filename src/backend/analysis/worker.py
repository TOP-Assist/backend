# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Module for setting up each worker process.
"""
from typing import Optional

from backend.analysis.schemas import AnalysisResult, BarrierDescription, OperatorResult, OperatorRequest
from backend.analysis.service import AnalysisService
from backend.parlance.schemas import ParlanceWord

_service: AnalysisService | None = None


def initialize_worker(model_name: str):
    """Initialization function for the analysis worker."""
    global _service
    import torch

    torch.set_num_threads(1)

    import spacy
    from limes.analyzers.de import GermanAnalyzer
    from limes.parsers import SpacyParser

    spacy.require_cpu()  # pyright: ignore[reportPrivateImportUsage]

    _service = AnalysisService(
        parser=SpacyParser(model=model_name),
        analyzer=GermanAnalyzer(),
    )


def get_service() -> AnalysisService:
    if _service is None:
        raise RuntimeError("Analysis worker is not initialized")
    return _service


def analyze_text(
    text: str,
    parlance_words: list[ParlanceWord] | None = None,
    check_barriers: bool = True,
) -> AnalysisResult:
    return get_service().analyze(
        text,
        check_barriers=check_barriers,
        parlance_words=parlance_words,
    )


def get_barrier_definitions() -> list[BarrierDescription]:
    return get_service().get_barrier_definitions()


def get_operators(request: OperatorRequest) -> OperatorResult:
    return get_service().get_operators(request)
