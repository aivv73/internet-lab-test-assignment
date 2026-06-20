from pathlib import Path
from typing import Any, cast

import httpx
import pytest

from app.core.config import Settings
from app.handlers.resend_client import ResendClient, ResendDeliveryError
from app.repositories.outbox_repository import OutboxRepository
from app.schemas.ai import AIAnalysis
from app.schemas.contact import ContactRequest
from app.schemas.email import EmailMessageData
from app.services.email_service import EmailService, SMTPProvider


def contact_request() -> ContactRequest:
    return ContactRequest.model_validate(
        {
            "name": "Ivan Petrov",
            "email": "ivan@example.com",
            "phone": "+7 999 123-45-67",
            "comment": "Hello! I want to discuss backend API development for my project.",
        }
    )


def ai_analysis() -> AIAnalysis:
    return AIAnalysis(
        category="project_inquiry",
        sentiment="positive",
        summary="User wants to discuss backend API development.",
        priority="normal",
        confidence=0.9,
        fallback_used=False,
    )


class SuccessfulSMTPClient:
    is_configured = True

    def __init__(self) -> None:
        self.sent_messages: list[EmailMessageData] = []

    async def send(self, message: EmailMessageData) -> None:
        self.sent_messages.append(message)


class FailingSMTPClient:
    is_configured = True

    async def send(self, _message: EmailMessageData) -> None:
        raise RuntimeError("SMTP failure")


class SuccessfulResendHttpClient:
    def __init__(self) -> None:
        self.requests: list[dict[str, object]] = []

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, object],
    ) -> httpx.Response:
        self.requests.append({"url": url, "headers": headers, "json": json})
        return httpx.Response(200, json={"id": "email_123"}, request=httpx.Request("POST", url))


class FailingResendHttpClient:
    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, object],
    ) -> httpx.Response:
        return httpx.Response(
            401,
            json={"message": "invalid api key"},
            request=httpx.Request("POST", url),
        )


def settings(tmp_path: Path, *, smtp_host: str | None = None) -> Settings:
    return Settings(
        storage_dir=tmp_path,
        log_file=tmp_path / "app.log",
        contact_owner_email="owner@example.com",
        email_from="no-reply@example.com",
        smtp_host=smtp_host,
    )


def resend_settings(tmp_path: Path, *, api_key: str | None = "resend-secret") -> Settings:
    return Settings(
        storage_dir=tmp_path,
        log_file=tmp_path / "app.log",
        contact_owner_email="owner@example.com",
        email_from="onboarding@resend.dev",
        email_provider="resend",
        resend_api_key=api_key,
    )


@pytest.mark.asyncio
async def test_email_service_queues_messages_when_smtp_is_not_configured(tmp_path: Path) -> None:
    outbox = OutboxRepository(tmp_path)
    service = EmailService(settings(tmp_path), outbox)

    delivery_status = await service.send_contact_emails(contact_request(), ai_analysis())

    queued_messages = outbox.list_all()
    assert delivery_status == "queued"
    assert len(queued_messages) == 2
    assert {message["to"] for message in queued_messages} == {
        "owner@example.com",
        "ivan@example.com",
    }
    assert all(message["reason"] == "SMTP is not configured." for message in queued_messages)


@pytest.mark.asyncio
async def test_email_service_queues_both_messages_when_smtp_fails(tmp_path: Path) -> None:
    outbox = OutboxRepository(tmp_path)
    service = EmailService(
        settings(tmp_path, smtp_host="smtp.example.com"),
        outbox,
        smtp_client=cast(SMTPProvider, FailingSMTPClient()),
    )

    delivery_status = await service.send_contact_emails(contact_request(), ai_analysis())

    queued_messages = outbox.list_all()
    assert delivery_status == "queued"
    assert len(queued_messages) == 2
    assert all(message["reason"] == "SMTP delivery failed." for message in queued_messages)


@pytest.mark.asyncio
async def test_email_service_sends_owner_and_user_emails_when_smtp_succeeds(
    tmp_path: Path,
) -> None:
    outbox = OutboxRepository(tmp_path)
    smtp_client = SuccessfulSMTPClient()
    service = EmailService(
        settings(tmp_path, smtp_host="smtp.example.com"),
        outbox,
        smtp_client=cast(SMTPProvider, smtp_client),
    )

    delivery_status = await service.send_contact_emails(contact_request(), ai_analysis())

    assert delivery_status == "sent"
    assert outbox.list_all() == []
    assert len(smtp_client.sent_messages) == 2
    assert str(smtp_client.sent_messages[0].to) == "owner@example.com"
    assert str(smtp_client.sent_messages[1].to) == "ivan@example.com"
    assert "AI analysis" in smtp_client.sent_messages[0].body
    assert "project_inquiry" in smtp_client.sent_messages[0].body


@pytest.mark.asyncio
async def test_email_service_queues_messages_when_resend_is_not_configured(
    tmp_path: Path,
) -> None:
    outbox = OutboxRepository(tmp_path)
    service = EmailService(resend_settings(tmp_path, api_key=None), outbox)

    delivery_status = await service.send_contact_emails(contact_request(), ai_analysis())

    queued_messages = outbox.list_all()
    assert delivery_status == "queued"
    assert len(queued_messages) == 2
    assert all(message["reason"] == "Resend is not configured." for message in queued_messages)


@pytest.mark.asyncio
async def test_resend_client_posts_plain_text_email() -> None:
    http_client = SuccessfulResendHttpClient()
    resend_client = ResendClient(
        Settings(
            email_from="onboarding@resend.dev",
            resend_api_key="resend-secret",
        ),
        http_client=cast(Any, http_client),
    )

    await resend_client.send(
        EmailMessageData(to="owner@example.com", subject="Subject", body="Plain text body")
    )

    assert len(http_client.requests) == 1
    request = http_client.requests[0]
    assert request["url"] == "https://api.resend.com/emails"
    assert request["headers"] == {
        "Authorization": "Bearer resend-secret",
        "Content-Type": "application/json",
    }
    assert request["json"] == {
        "from": "onboarding@resend.dev",
        "to": ["owner@example.com"],
        "subject": "Subject",
        "text": "Plain text body",
    }


@pytest.mark.asyncio
async def test_resend_client_raises_delivery_error_on_http_failure() -> None:
    resend_client = ResendClient(
        Settings(
            email_from="onboarding@resend.dev",
            resend_api_key="resend-secret",
        ),
        http_client=cast(Any, FailingResendHttpClient()),
    )

    with pytest.raises(ResendDeliveryError):
        await resend_client.send(
            EmailMessageData(to="owner@example.com", subject="Subject", body="Plain text body")
        )
