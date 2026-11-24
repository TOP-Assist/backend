# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Components to be used for Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from backend.feedback.service import FeedbackConfigService, FeedbackService
from backend.infra.mongo import MongoDBDep


async def get_feedback_service(db: MongoDBDep) -> FeedbackService:
    return FeedbackService(collection=db["feedback"])


FeedbackServiceDep = Annotated[
    FeedbackService,
    Depends(get_feedback_service),
]

async def get_feedback_config_service(
    db: MongoDBDep,
) -> FeedbackConfigService:
    """Provide the service for feedback configuration data."""
    return FeedbackConfigService(collection=db["feedback_categories"])


FeedbackConfigServiceDep = Annotated[
    FeedbackConfigService,
    Depends(get_feedback_config_service),
]