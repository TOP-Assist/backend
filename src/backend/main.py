"""Entrypoint for the fastAPI application."""

import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from backend.analysis.executor import AnalysisExecutor
from backend.analysis.routes import router as analysis_router
from backend.analysis.worker import initialize_worker
from backend.config import Settings
from backend.feedback.routes import router as feedback_router
from backend.logging import configure_logging
from backend.parlance.routes import router as parlance_router
from backend.translation.routes import router as translation_router

API_PREFIX = "/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up components that each fastAPI worker should own throughout their
    lifetime.
    """
    # Pyright doesn't play nice for required env vars so we have to shush it.
    settings = Settings()  # pyright: ignore[reportCallIssue]
    app.state.settings = settings
    configure_logging(settings.log_level)

    mongo_client = AsyncMongoClient(
        settings.mongodb_uri.get_secret_value(),
        serverSelectionTimeoutMS=(settings.mongodb_server_selection_timeout_ms),
    )

    try:
        pool = ProcessPoolExecutor(
            max_workers=settings.analysis_num_workers,
            mp_context=multiprocessing.get_context("spawn"),
            initializer=initialize_worker,
            initargs=(settings.analysis_model,),
        )
        executor = AnalysisExecutor(pool, max_outstanding=2)
        # Start the worker, load the model, and performs warm inference.
        # Startup fails if initialization or inference fails.
        _ = await executor.analyze("Das ist ein kurzer Beispielsatz.")
        app.state.analysis_exec = executor

        # Fail startup if MongoDB is unavailable.
        await mongo_client.admin.command("ping")
        app.state.mongodb = mongo_client[settings.mongodb_database]
        # Load domains on startup to avoid DB hits for static information.
        app.state.domains = app.state.mongodb["parlance"].distinct("domain")

        yield
    finally:
        await mongo_client.close()

        await asyncio.to_thread(
            pool.shutdown,
            wait=True,
            cancel_futures=True,
        )


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(analysis_router, prefix=API_PREFIX)
app.include_router(feedback_router, prefix=API_PREFIX)
app.include_router(parlance_router, prefix=API_PREFIX)
app.include_router(translation_router, prefix=API_PREFIX)
