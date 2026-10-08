"""Entrypoint for the fastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from backend.analysis.routes import router as analysis_router
from backend.config import Settings
from backend.feedback.routes import router as feedback_router
from backend.logging import configure_logging
from backend.parlance.routes import router as parlance_router
from backend.translation.routes import router as translation_router

API_PREFIX = "/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pyright doesn't play nice for required env vars so we have to shush it.
    settings = Settings()  # pyright: ignore[reportCallIssue]
    configure_logging(settings.log_level)
    mongo_client = AsyncMongoClient(
        settings.mongodb_uri.get_secret_value(),
        serverSelectionTimeoutMS=(settings.mongodb_server_selection_timeout_ms),
    )

    try:
        # Fail startup if MongoDB is unavailable.
        await mongo_client.admin.command("ping")
        app.state.mongodb = mongo_client[settings.mongodb_database]
        # Load domains on startup to avoid DB hits for static information.
        app.state.domains = app.state.mongodb["parlance"].distinct("domain")
        yield
    finally:
        await mongo_client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(analysis_router, prefix=API_PREFIX)
app.include_router(feedback_router, prefix=API_PREFIX)
app.include_router(parlance_router, prefix=API_PREFIX)
app.include_router(translation_router, prefix=API_PREFIX)
