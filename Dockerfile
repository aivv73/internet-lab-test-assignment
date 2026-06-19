# syntax=docker/dockerfile:1.7

FROM node:24-slim AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    FRONTEND_DIST_DIR=/app/frontend/dist/frontend/browser \
    STORAGE_DIR=/app/storage \
    LOG_FILE=/app/storage/logs/app.log

WORKDIR /app

RUN pip install --no-cache-dir "poetry>=2,<3"

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-ansi

COPY app ./app
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/storage/logs \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
