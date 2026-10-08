"""Entrypoint for the fastAPI application."""

from fastapi import FastAPI

from backend.analysis.routes import router as analysis_router
from backend.feedback.routes import router as feedback_router
from backend.parlance.routes import router as parlance_router
from backend.translation.routes import router as translation_router

API_PREFIX = "/v1"
app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(analysis_router, prefix=API_PREFIX)
app.include_router(feedback_router, prefix=API_PREFIX)
app.include_router(parlance_router, prefix=API_PREFIX)
app.include_router(translation_router, prefix=API_PREFIX)
