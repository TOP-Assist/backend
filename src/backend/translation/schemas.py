"""Object definitions for translation/text simplification functionality."""

from enum import StrEnum

from pydantic import BaseModel


class TranslationStrategy(StrEnum):
    """
    The type of strategy according to which translation should be performed.
    """

    AUTO = "auto"


class TranslationRequest(BaseModel):
    """A user request for translation."""

    text: str
    strategy: TranslationStrategy = TranslationStrategy.AUTO


class TranslationExample(BaseModel):
    """An example text pair that was used as context in the translation."""

    id: str
    similarity: float


class TranslationResult(BaseModel):
    """The result of a translation attempt."""

    title: str
    optimized: str
    explanation: str
    answer: str
    strategy_used: TranslationStrategy
    examples: list[TranslationExample] | None = None
    example_similarities: list[float] = []
