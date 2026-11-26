# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM docker.io/library/python:3.14-slim-trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends git git-lfs ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies separately to cache them across source changes.
COPY pyproject.toml uv.lock README.md ./
COPY LICENSES/ ./LICENSES/
# Hatchling can read project metadata during either sync. CI supplies VERSION
# because .git is excluded from the build context.
ARG VERSION=0.0.0+local
RUN UV_DYNAMIC_VERSIONING_BYPASS="${VERSION}" \
    uv sync --locked --no-dev --no-install-project --no-cache

# Install the application as a regular, non-editable package.
COPY src/ ./src/
RUN UV_DYNAMIC_VERSIONING_BYPASS="${VERSION}" \
    uv sync --locked --no-dev --no-editable --no-cache

# Run as an unprivileged numeric user.
USER 10001:10001

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
