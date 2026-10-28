# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Entrypoint for the fastAPI application."""

import asyncio
import multiprocessing
from collections.abc import AsyncGenerator
from concurrent.futures import ProcessPoolExecutor
from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient

from backend.analysis.executor import AnalysisExecutor
from backend.analysis.routes import router as analysis_router
from backend.analysis.worker import initialize_worker
from backend.config import Settings
from backend.feedback.routes import router as feedback_router
from backend.logging import configure_logging
from backend.parlance.routes import router as parlance_router
from backend.translation.client import OpenAICompatibleTranslationClient
from backend.translation.routes import router as translation_router
from backend.translation.service import TranslationService

API_PREFIX = "/v1"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Initialize resources owned by this API worker."""
    settings = Settings()  # pyright: ignore[reportCallIssue]
    app.state.settings = settings
    configure_logging(settings.log_level)

    async with AsyncExitStack() as stack:
        # Register mongoDB components.
        mongo_client = AsyncMongoClient(
            settings.mongodb_uri.get_secret_value(),
            serverSelectionTimeoutMS=(
                settings.mongodb_server_selection_timeout_ms
            ),
        )
        stack.push_async_callback(mongo_client.close)
        await mongo_client.admin.command("ping")
        mongodb = mongo_client[settings.mongodb_database]
        app.state.mongodb = mongodb
        app.state.domains = await mongodb["parlance"].distinct("domain")

        # Register `analysis` components.
        pool = ProcessPoolExecutor(
            max_workers=settings.analysis_num_workers,
            mp_context=multiprocessing.get_context("spawn"),
            initializer=initialize_worker,
            initargs=(settings.analysis_model,),
        )
        stack.push_async_callback(
            asyncio.to_thread,
            pool.shutdown,
            wait=True,
            cancel_futures=True,
        )
        executor = await AnalysisExecutor.create(pool, max_outstanding=2)
        _ = await executor.analyze("Das ist ein kurzer Beispielsatz.")
        app.state.analysis_executor = executor

        # Register `translation` components.
        sdk = await stack.enter_async_context(
            AsyncOpenAI(
                base_url=settings.llm_base_url,
                api_key=settings.llm_api_key.get_secret_value(),
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
            )
        )
        translation_client = OpenAICompatibleTranslationClient(
            sdk,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        )
        app.state.translation_service = TranslationService(
            client=translation_client,
        )

        yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(analysis_router, prefix=API_PREFIX)
app.include_router(feedback_router, prefix=API_PREFIX)
app.include_router(parlance_router, prefix=API_PREFIX)
app.include_router(translation_router, prefix=API_PREFIX)
