"""HTTP route definitions for feedback functionality."""

from fastapi import APIRouter

from backend.feedback.schemas import TranslationFeedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", status_code=201)
async def post_feedback(feedback: TranslationFeedback):
    """
    Store feedback or suggestion in the database."""
    # TODO: Implement feedback-posting.
    raise NotImplementedError
