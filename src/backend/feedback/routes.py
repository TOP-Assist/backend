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
