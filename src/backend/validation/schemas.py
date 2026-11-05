from typing import Any

from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    input_text: str
    output_text: str

    selected_validators: str = "all"


class ValidationResult(BaseModel):
    """Translation Validation Result for a single metric"""

    metric: str = Field(
        ...,
        description="The validation metric for which the score is reported",
    )

    score: float = Field(
        ...,
        description="The validation score for a specific translation & metric",
    )

    meta: dict[str, Any] = Field(
        ...,
        description="Additional metadata that might be relevant for a specific evaluation metric."
    )

class TranslationValidation(BaseModel):
    """Translation Validation Result for all metrics for one Translation"""
    translation_id: str     # TODO: Is this stored?
    results: dict[str, ValidationResult] = Field(default_factory=dict)
