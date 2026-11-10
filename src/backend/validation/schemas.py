from typing import Any, Optional

from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    input_text: str = Field(
        ...,
        description="The input text containing the task to be translated.",
    )
    output_text: str = Field(
        ...,
        description="The resulting translation for the input task.",
    )

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

    parameters: dict[str, Any] = Field(
        ...,
        description="Parametrization of the validation function used.",
    )

    meta: dict[str, Any] = Field(
        ...,
        description="Additional metadata that might be relevant for a specific evaluation metric."
    )

class TranslationValidation(BaseModel):
    """Translation Validation Result for all metrics for one Translation"""
    results: dict[str, ValidationResult] = Field(default_factory=dict)
    translation_id: Optional[str] = None  # TODO: Is this stored?
    inserted_id: Optional[str] = None
