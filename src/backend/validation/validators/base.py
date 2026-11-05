from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ValidatorResult(BaseModel):
    score: float
    meta: dict[str, Any]

class Validator(ABC):
    def __init__(self, input: str, output: str):
        self.input = input
        self.output = output

    @abstractmethod
    def run(self, **kwargs) -> ValidatorResult:
        ...