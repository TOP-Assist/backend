"""Entrypoint for the fastAPI application."""

from fastapi import FastAPI

API_PREFIX = "/v1"
app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
