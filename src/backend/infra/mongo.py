"""Module for managing MongoDB database connection objects."""

from typing import Annotated, Any

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase


async def get_mongodb(request: Request) -> AsyncDatabase[dict[str, Any]]:
    return request.app.state.db


MongoDBDep = Annotated[
    AsyncDatabase[dict[str, Any]],
    Depends(get_mongodb),
]
