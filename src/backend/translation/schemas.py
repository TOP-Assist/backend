# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Object definitions for translation/text simplification functionality."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.analysis.schemas import BarrierTokenHighlight


class TranslationStrategy(StrEnum):
    """
    The type of strategy according to which translation should be performed.
    """

    DEFAULT = "default"


class TranslationRequest(BaseModel):
    """A user request for translation."""

    text: str
    strategy: TranslationStrategy = TranslationStrategy.DEFAULT
    barriers: list[BarrierTokenHighlight] | None = None
    parlance_words: list[str] | None = None


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


class LLMAnswer(BaseModel):
    """
    Model that will be used by the LLM for output validation.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Title of the task.")
    optimized: str = Field(
        description="Linguistically simplified version of the task."
    )
    explanation: str = Field(
        description="Explanation of what was simplified and why."
    )
    answer: str = Field(description="Answer to the question or subtasks.")
