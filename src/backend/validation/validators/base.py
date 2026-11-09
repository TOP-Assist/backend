from abc import ABC, abstractmethod
from typing import Any, Optional

from backend.validation.schemas import ValidationResult


class Validator(ABC):
    _registry_name: str

    @abstractmethod
    async def run(self, inp: str, out: str, meta: Optional[dict[str, Any]]) -> ValidationResult:
        ...