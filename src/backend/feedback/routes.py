# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""HTTP route definitions for feedback functionality."""

from fastapi import APIRouter

from backend.feedback.deps import FeedbackServiceDep
from backend.feedback.schemas import TranslationFeedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", status_code=201)
async def post_feedback(
    service: FeedbackServiceDep,
    feedback: TranslationFeedback,
):
    """Store feedback in the database."""
    _ = await service.store_feedback(feedback)
