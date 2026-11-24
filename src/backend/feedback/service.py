# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Service class for feedback functionality."""

from datetime import UTC, datetime
from typing import Any

from pymongo import DESCENDING
from pymongo.asynchronous.collection import AsyncCollection

from backend.feedback.schemas import (
    FeedbackCategories,
    FeedbackCategoriesVersion,
    FeedbackMode,
    FeedbackContext,
)

class FeedbackService:
    """Service for interacting with feedback data."""

    def __init__(self, collection: AsyncCollection):
        self._collection = collection

    async def store_feedback(self, feedback: FeedbackContext) -> str:
        """Store feedback and return its new id."""
        result = await self._collection.insert_one(feedback.model_dump())
        return str(result.inserted_id)

class FeedbackConfigService:
    """Service for interacting with feedback configuration data."""

    def __init__(self, collection: AsyncCollection):
        self._collection = collection

    async def get_feedback_categories(
        self,
        feedback_mode: FeedbackMode,
        version: int | None = None,
    ) -> FeedbackCategoriesVersion | None:
        """Retrieve the latest or a specific category version."""
        query: dict[str, Any] = {"feedback_mode": feedback_mode}

        if version is not None:
            query["version"] = version

        doc = await self._collection.find_one(
            query,
            projection={"_id": 0},
            sort=[("version", DESCENDING)],
        )

        assert doc not in (None, {}), f"Feedback categories with mode {feedback_mode} and version {version} not found."

        doc["timestamp"] = doc["timestamp"].replace(tzinfo=UTC)

        return FeedbackCategoriesVersion.model_validate(doc)