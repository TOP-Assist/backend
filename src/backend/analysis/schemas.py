# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Object definitions for text analysis functionality."""

from typing import Self, Optional

from pydantic import BaseModel, Field, model_validator

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
    check_barriers: bool = True

    @model_validator(mode="after")
    def check_analysis_is_requested(self) -> Self:
        """
        Ensure that the request actually contains a request for analysis to rule
        out cases where the client sends a request that contains no parlance
        and asks to omit barrier analysis.
        """
        if self.parlance_words is None and not self.check_barriers:
            raise ValueError(
                "The request requested neither parlance nor barrier analysis."
            )
        return self


class AnalysisResult(BaseModel):
    """The result of a text complexity analysis."""

    text: str
    barriers: list[BarrierTokenHighlight] | None
    parlance: list[TokenHighlight] | None

class OperatorRequest(BaseModel):
    input: str = Field(
        ...,
        description="The input text in which the Operators should be identified.",
    )
    operators: Optional[list[str]] = Field(
        None,
        description="An optional set of operators for which the search should be performed. Will be lemmatized automatically."
    )

class OperatorResult(BaseModel):
    operators: list[str] = Field(
        ...,
        description="Resulting list of operators found in a given input."
    )