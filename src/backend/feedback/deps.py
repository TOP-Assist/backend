"""Components to be used for Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from backend.feedback.service import FeedbackService
from backend.infra.mongo import MongoDBDep


async def get_feedback_service(db: MongoDBDep) -> FeedbackService:
    return FeedbackService(collection=db["feedback"])


FeedbackServiceDep = Annotated[
    FeedbackService,
    Depends(get_feedback_service),
]
