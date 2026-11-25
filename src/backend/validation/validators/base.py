# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import Generic, Self, TypeVar

from pydantic import BaseModel

from backend.analysis.executor import AnalysisExecutor
from backend.validation.schemas import ValidationRequest, ValidationResult


class ValidatorParametrization(BaseModel):
    pass


P = TypeVar("P", bound=ValidatorParametrization)


class Validator(ABC, Generic[P]):  # noqa: UP046
    _parametrization: P

    def __init__(self, parametrization: P):
        self.parametrization = parametrization

    @abstractmethod
    async def run(self, request: ValidationRequest) -> ValidationResult: ...

    @classmethod
    def create(
        cls,
        parametrization: P,
        analysis_executor: AnalysisExecutor,
    ) -> Self:
        # Ignore analysis executor by default, overwrite in child if required
        return cls(parametrization)

    def get_parametrization(self) -> P:
        return self._parametrization
