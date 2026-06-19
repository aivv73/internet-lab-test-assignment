from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.main import create_app
from app.schemas.ai import AIAnalysis, fallback_ai_analysis
from app.schemas.contact import ContactRequest


def valid_contact_payload() -> dict[str, str]:
    return {
        "name": "Ivan Petrov",
        "email": "ivan@example.com",
        "phone": "+7 999 123-45-67",
        "comment": "Hello! I want to discuss backend API development for my project.",
    }


def test_contact_request_trims_strings_and_accepts_valid_payload() -> None:
    payload = valid_contact_payload() | {"name": "  Ivan Petrov  "}

    request = ContactRequest.model_validate(payload)

    assert request.name == "Ivan Petrov"
    assert str(request.email) == "ivan@example.com"


def test_contact_request_rejects_unknown_fields() -> None:
    payload = valid_contact_payload() | {"company": "InternetLab"}

    with pytest.raises(ValidationError):
        ContactRequest.model_validate(payload)


def test_contact_endpoint_rejects_invalid_payload() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/api/contact",
        json=valid_contact_payload() | {"email": "not-an-email", "comment": "short"},
    )

    assert response.status_code == 422


def test_contact_endpoint_contract_is_exposed_in_openapi() -> None:
    app = create_app()
    client = TestClient(app)

    openapi = client.get("/openapi.json").json()

    contact_post = openapi["paths"]["/api/contact"]["post"]
    assert "202" in contact_post["responses"]
    assert contact_post["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ContactRequest"
    )


def test_ai_fallback_matches_contract() -> None:
    fallback = fallback_ai_analysis()

    assert isinstance(fallback, AIAnalysis)
    assert fallback.category == "unknown"
    assert fallback.sentiment == "unknown"
    assert fallback.priority == "normal"
    assert fallback.confidence == 0.0
    assert fallback.fallback_used is True


def test_metrics_endpoint_is_open_when_api_key_is_not_configured(tmp_path: Path) -> None:
    settings = Settings(metrics_api_key=None, log_file=tmp_path / "app.log")
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.get("/api/metrics")

    assert response.status_code == 200
    assert response.json()["total_submissions"] == 0


def test_metrics_endpoint_requires_api_key_when_configured(tmp_path: Path) -> None:
    settings = Settings(metrics_api_key="secret", log_file=tmp_path / "app.log")
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    missing_key_response = client.get("/api/metrics")
    valid_key_response = client.get("/api/metrics", headers={"X-API-Key": "secret"})

    assert missing_key_response.status_code == 401
    assert valid_key_response.status_code == 200
