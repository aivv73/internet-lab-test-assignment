from pathlib import Path
from typing import cast

import pytest

from app.core.config import Settings
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


def settings(tmp_path: Path, *, smtp_host: str | None = None) -> Settings:
    return Settings(
        storage_dir=tmp_path,
        log_file=tmp_path / "app.log",
        contact_owner_email="owner@example.com",
        email_from="no-reply@example.com",
        smtp_host=smtp_host,
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
