"""Service class for feedback functionality."""

from pymongo.asynchronous.collection import AsyncCollection

from backend.feedback.schemas import TranslationFeedback


class FeedbackService:
    """Service for interacting with feedback data."""

    def __init__(self, collection: AsyncCollection):
        self._collection = collection

    async def store_feedback(self, feedback: TranslationFeedback) -> str:
        """Store feedback and return its new id."""
        result = await self._collection.insert_one(feedback.model_dump())
        return result.inserted_id
