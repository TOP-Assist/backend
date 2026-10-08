"""Components to be used for Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from backend.infra.mongo import MongoDBDep
from backend.parlance.service import ParlanceService


async def get_parlance_service(db: MongoDBDep) -> ParlanceService:
    return ParlanceService(collection=db["parlance"])


ParlanceServiceDep = Annotated[
    ParlanceService,
    Depends(get_parlance_service),
]
