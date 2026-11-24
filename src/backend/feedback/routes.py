# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""HTTP route definitions for feedback functionality."""

from fastapi import APIRouter, HTTPException

from backend.feedback.deps import FeedbackConfigServiceDep, FeedbackServiceDep
from backend.feedback.schemas import (
    FeedbackCategoriesVersion,
    FeedbackContext,
    FeedbackMode,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", status_code=201)
async def post_feedback(
    service: FeedbackServiceDep,
    feedback: FeedbackContext,
):
    """Store feedback in the database."""
    _ = await service.store_feedback(feedback)

@router.get("/categories")
async def get_feedback_categories(
    service: FeedbackConfigServiceDep,
    feedback_mode: FeedbackMode,
    version: int | None = None,
) -> FeedbackCategoriesVersion:
    """Retrieve the latest or a specific category version."""
    categories = await service.get_feedback_categories(
        feedback_mode, version
    )

    if categories is None:
        raise HTTPException(
            status_code=404,
            detail="Feedback categories not found.",
        )

    return categories