FROM docker.io/library/python:3.14-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies separately to cache them across source changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project --no-cache

# Install the application as a regular, non-editable package.
COPY README.md ./
COPY src/ ./src/
RUN uv sync --locked --no-dev --no-editable --no-cache

# Run as an unprivileged numeric user.
USER 10001:10001

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
