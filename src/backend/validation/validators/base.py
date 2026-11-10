from abc import ABC, abstractmethod

from pydantic import BaseModel

from backend.validation.schemas import ValidationResult, ValidationRequest


class Validator(ABC):
    parametrization: BaseModel

    @abstractmethod
    async def run(self, request: ValidationRequest) -> ValidationResult:
        ...

    def _params_to_dict(self) -> dict:
        return self.parametrization.model_dump()
