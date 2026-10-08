"""Object definitions for feedback functionality."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.translation.schemas import TranslationStrategy


class UserRating(BaseModel):
    """User rating of a translation."""

    ratings: dict[str, int] = Field(
        ...,
        description="Categories and rating from 1-5; 0 means not rated",
    )
    comment: str | None = Field(
        None,
        description="Additional comment from the user",
    )
    suggestion: str | None = Field(
        None,
        description="User suggestion for improvement",
    )
    mode: str | None = Field(
        None,
        description=(
            "The mode in which the feedback was given, e.g., 'translation' or "
            "'barrier_analysis'"
        ),
    )
    barriers: list[str] | None = Field(
        None,
        description="List of barriers identified by the user, if applicable",
    )


class TranslationFeedback(BaseModel):
    """
    User-provided feedback on a translation.
    """

    normal_text: str = Field(..., description="Original text.")
    top_text: str = Field(..., description="Translated text.")
    strategy: TranslationStrategy = Field(
        ...,
        description="Translation strategy that was applied to the text.",
    )
    feedback: UserRating = Field(
        ...,
        description="User-provided rating of the translation quality.",
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
