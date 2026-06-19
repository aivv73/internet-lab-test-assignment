from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


def valid_contact_payload() -> dict[str, str]:
    return {
        "name": "Ivan Petrov",
        "email": "ivan@example.com",
        "phone": "+7 999 123-45-67",
        "comment": "Hello! I want to discuss backend API development for my project.",
    }


def make_client(tmp_path: Path, *, metrics_api_key: str | None = None) -> TestClient:
    settings = Settings(
        storage_dir=tmp_path,
        log_file=tmp_path / "app.log",
        contact_owner_email="owner@example.com",
        email_from="no-reply@example.com",
        ai_api_key=None,
        metrics_api_key=metrics_api_key,
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


def test_metrics_api_returns_empty_defaults(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/metrics")

    assert response.status_code == 200
    assert response.json() == {
        "total_submissions": 0,
        "by_category": {},
        "by_sentiment": {},
        "email_delivery": {},
        "ai_fallbacks": 0,
    }


def test_metrics_api_returns_aggregates_after_contact_submission(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    contact_response = client.post("/api/contact", json=valid_contact_payload())
    metrics_response = client.get("/api/metrics")

    assert contact_response.status_code == 202
    assert metrics_response.status_code == 200
    assert metrics_response.json() == {
        "total_submissions": 1,
        "by_category": {"unknown": 1},
        "by_sentiment": {"unknown": 1},
        "email_delivery": {"queued": 1},
        "ai_fallbacks": 1,
    }


def test_metrics_api_requires_key_when_configured(tmp_path: Path) -> None:
    client = make_client(tmp_path, metrics_api_key="secret")

    missing_key_response = client.get("/api/metrics")
    wrong_key_response = client.get("/api/metrics", headers={"X-API-Key": "wrong"})
    valid_key_response = client.get("/api/metrics", headers={"X-API-Key": "secret"})

    assert missing_key_response.status_code == 401
    assert wrong_key_response.status_code == 401
    assert valid_key_response.status_code == 200
