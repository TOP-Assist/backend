from abc import ABC, abstractmethod
from typing import Optional, Self, Generic, TypeVar

from backend.analysis.executor import AnalysisExecutor
from pydantic import BaseModel

from backend.validation.schemas import ValidationResult, ValidationRequest


class ValidatorParametrization(BaseModel):
    pass

P = TypeVar("P", bound=ValidatorParametrization)

class Validator(ABC, Generic[P]):
    _parametrization: P

    def __init__(self, parametrization: ValidatorParametrization):
        self.parametrization = parametrization

    @abstractmethod
    async def run(self, request: ValidationRequest) -> ValidationResult:
        ...

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