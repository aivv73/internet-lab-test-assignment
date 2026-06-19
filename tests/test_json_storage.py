from pathlib import Path

import pytest

from app.core.errors import StorageError
from app.repositories.json_file import JsonFileRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.rate_limit_repository import RateLimitRepository
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.ai import fallback_ai_analysis


def test_json_file_repository_writes_and_reads_json(tmp_path: Path) -> None:
    repository = JsonFileRepository(tmp_path)
    path = tmp_path / "nested" / "data.json"

    repository.write_json(path, {"hello": "world"})

    assert repository.read_json(path) == {"hello": "world"}


def test_json_file_repository_returns_default_for_missing_file(tmp_path: Path) -> None:
    repository = JsonFileRepository(tmp_path)

    assert repository.read_json(tmp_path / "missing.json", default={"items": 0}) == {"items": 0}


def test_json_file_repository_raises_storage_error_for_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("not-json", encoding="utf-8")

    repository = JsonFileRepository(tmp_path)

    with pytest.raises(StorageError):
        repository.read_json(path)


def test_submission_repository_saves_and_lists_submissions(tmp_path: Path) -> None:
    repository = SubmissionRepository(tmp_path)
    submission = {"id": "submission-1", "name": "Ivan"}

    repository.save("submission-1", submission)

    assert repository.get("submission-1") == submission
    assert repository.list_all() == [submission]
    assert repository.get("missing") is None


def test_outbox_repository_queues_messages(tmp_path: Path) -> None:
    repository = OutboxRepository(tmp_path)

    message_id = repository.enqueue(
        {"to": "user@example.com", "subject": "Hello", "body": "Message body"}
    )

    messages = repository.list_all()
    assert len(messages) == 1
    assert messages[0]["id"] == message_id
    assert messages[0]["to"] == "user@example.com"
    assert "queued_at" in messages[0]


def test_metrics_repository_returns_defaults_and_records_submission(tmp_path: Path) -> None:
    repository = MetricsRepository(tmp_path)

    initial_metrics = repository.get()
    assert initial_metrics.total_submissions == 0

    updated_metrics = repository.record_submission(fallback_ai_analysis(), "queued")

    assert updated_metrics.total_submissions == 1
    assert updated_metrics.by_category == {"unknown": 1}
    assert updated_metrics.by_sentiment == {"unknown": 1}
    assert updated_metrics.email_delivery == {"queued": 1}
    assert updated_metrics.ai_fallbacks == 1
    assert repository.get() == updated_metrics


def test_rate_limit_repository_saves_and_loads_state(tmp_path: Path) -> None:
    repository = RateLimitRepository(tmp_path)
    state = {"ip:127.0.0.1": {"count": 1, "window_start": 123.0}}

    repository.save_state(state)

    assert repository.get_state() == state
