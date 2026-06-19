from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.submission_repository import SubmissionRepository


def valid_contact_payload() -> dict[str, str]:
    return {
        "name": "Ivan Petrov",
        "email": "ivan@example.com",
        "phone": "+7 999 123-45-67",
        "comment": "Hello! I want to discuss backend API development for my project.",
    }


def make_client(
    tmp_path: Path,
    *,
    rate_limit_ip_requests: int = 5,
    rate_limit_ip_window_seconds: int = 600,
    rate_limit_email_requests: int = 3,
) -> TestClient:
    settings = Settings(
        storage_dir=tmp_path,
        log_file=tmp_path / "app.log",
        contact_owner_email="owner@example.com",
        email_from="no-reply@example.com",
        ai_api_key=None,
        rate_limit_ip_requests=rate_limit_ip_requests,
        rate_limit_ip_window_seconds=rate_limit_ip_window_seconds,
        rate_limit_email_requests=rate_limit_email_requests,
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


def test_contact_workflow_accepts_submission_with_ai_and_email_fallbacks(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post("/api/contact", json=valid_contact_payload())

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "accepted"
    assert body["email_delivery"] == "queued"
    assert body["ai"]["fallback_used"] is True

    submissions = SubmissionRepository(tmp_path).list_all()
    assert len(submissions) == 1
    assert submissions[0]["id"] == body["id"]
    assert submissions[0]["email_delivery"] == "queued"

    queued_messages = OutboxRepository(tmp_path).list_all()
    assert len(queued_messages) == 2

    metrics = MetricsRepository(tmp_path).get()
    assert metrics.total_submissions == 1
    assert metrics.ai_fallbacks == 1
    assert metrics.email_delivery == {"queued": 1}


def test_contact_workflow_returns_429_when_rate_limit_is_exceeded(tmp_path: Path) -> None:
    client = make_client(
        tmp_path,
        rate_limit_ip_requests=1,
        rate_limit_ip_window_seconds=600,
        rate_limit_email_requests=10,
    )

    first_response = client.post("/api/contact", json=valid_contact_payload())
    second_response = client.post(
        "/api/contact",
        json=valid_contact_payload() | {"email": "other@example.com"},
    )

    assert first_response.status_code == 202
    assert second_response.status_code == 429
    assert second_response.json()["error"]["code"] == "rate_limit_exceeded"

    submissions = SubmissionRepository(tmp_path).list_all()
    assert len(submissions) == 1
