"""Object definitions for text analysis functionality."""

from pydantic import BaseModel, Field

from backend.parlance.schemas import ParlanceWord


class BarrierDescription(BaseModel):
    """A basic description of a text barrier."""

    title: str
    description: str


class TokenHighlight(BaseModel):
    """
    A token to be highlighted in a given source text.
    """

    start: int = Field(
        ...,
        description="Index of first character of token in the source string.",
    )
    end: int = Field(
        ...,
        description="Index of last character of token in the source string.",
    )
    token: str = Field(
        ...,
        description="The character sequence of the token.",
    )


class BarrierTokenHighlight(TokenHighlight):
    """
    A token to be highlighted in the context of a barrier.
    """

    title: str
    description: str
    suggestion: str
    barrier_number: int


class AnalysisRequest(BaseModel):
    """A user request for text complexity analysis."""

    text: str
    parlance_words: list[ParlanceWord] | None = None
    skip_barriers: bool = False


class AnalysisResult(BaseModel):
    """The result of a text complexity analysis."""

    text: str
    barriers: list[BarrierTokenHighlight]
    parlance: list[TokenHighlight]
