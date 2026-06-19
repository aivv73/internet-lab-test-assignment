.PHONY: install dev test lint format typecheck check

install:
	POETRY_KEYRING_ENABLED=false poetry install --no-root

dev:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run ty check

check: lint typecheck test
