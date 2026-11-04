# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

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
COPY LICENSES/ ./LICENSES/
COPY src/ ./src/
# .git is not part of the build context, so the package version cannot be read
# from the git tag here. CI passes it in as VERSION (see README, "Releases").
ARG VERSION=0.0.0+local
RUN UV_DYNAMIC_VERSIONING_BYPASS="${VERSION}" \
    uv sync --locked --no-dev --no-editable --no-cache

# Run as an unprivileged numeric user.
USER 10001:10001

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
