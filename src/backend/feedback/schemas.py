# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Object definitions for feedback functionality."""

from datetime import UTC, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.translation.schemas import TranslationStrategy

# The feedback mode for which the categories are defined.
# Extending the list of modes requires updating the validator below.
FeedbackMode = Literal["translation", "barrier_analysis"]

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
    mode: FeedbackMode | None = Field(
        None,
        description=(
            "The mode in which the feedback was given, e.g., 'translation' or "
            "'barrier_analysis'"
        ),
    )
    
class FeedbackContext(BaseModel):
    """
    User-provided context for feedback.
    """

    text_original: str = Field(..., description="Original text.")
    feedback: UserRating = Field(
        ...,
        description="User-provided rating of the translation quality.",
    )
    categories_version: int = Field(
        default=1,
        ge=1,
        description="Version of the feedback categories shown to the user.",
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    # additional fields for analysis feedback
    barriers: list[str] | None = Field(
        None,
        description="List of barriers identified by the user, if applicable",
    )
    operators: list[str] | None = Field(
        None,
        description="List of operators identified by the user, if applicable",
    )
    # additional fields for translation feedback
    text_translated: str | None = Field(None, description="Translated text.")
    strategy: TranslationStrategy = Field(
        ...,
        description="Translation strategy that was applied to the text.",
    )

class FeedbackCategories(BaseModel):
    """Rating categories for different feedback modes."""

    model_config = ConfigDict(extra="forbid")

    feedback_mode: FeedbackMode = Field(
        ..., description="The feedback mode for which the categories are defined."
    )
    categories: list[str] = Field(
        ..., description="List of category names for the feedback."
    )

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, categories: list[str]) -> list[str]:
        """Reject blank and duplicate category names within a mode."""
        if any(not name.strip() for name in categories):
            raise ValueError("Category names must not be blank.")

        if len(categories) != len(set(categories)):
            raise ValueError("Category names must be unique within a mode.")

        return categories


class FeedbackCategoriesVersion(FeedbackCategories):
    """A version of the feedback categories."""

    version: int = Field(ge=1)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
    )