from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ValidatorResult(BaseModel):
    score: float
    meta: dict[str, Any]

class Validator(ABC):
    def __init__(self):
        ...

    # TODO: **kwargs is in violation of Liskov
    @abstractmethod
    async def run(self, inp: str, out: str, **kwargs) -> ValidatorResult:
        ...