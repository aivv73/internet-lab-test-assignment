import logging
from typing import Protocol

from app.core.config import Settings
from app.handlers.resend_client import ResendClient
from app.handlers.smtp_client import SMTPClient
from app.repositories.json_file import JsonObject
from app.repositories.outbox_repository import OutboxRepository
from app.schemas.ai import AIAnalysis
from app.schemas.contact import ContactRequest, EmailDeliveryStatus
from app.schemas.email import EmailMessageData

logger = logging.getLogger("app.email")


class EmailProvider(Protocol):
    @property
    def is_configured(self) -> bool: ...

    async def send(self, message: EmailMessageData) -> None: ...


SMTPProvider = EmailProvider


class EmailService:
    """Send contact emails through SMTP or queue them to file outbox."""

    def __init__(
        self,
        settings: Settings,
        outbox_repository: OutboxRepository,
        smtp_client: EmailProvider | None = None,
    ) -> None:
        self._settings = settings
        self._outbox_repository = outbox_repository
        self._email_provider = smtp_client or _build_email_provider(settings)

    async def send_contact_emails(
        self,
        contact: ContactRequest,
        ai: AIAnalysis,
    ) -> EmailDeliveryStatus:
        messages = self._build_contact_messages(contact, ai)

        provider_name = _provider_name(self._email_provider)
        if not self._email_provider.is_configured:
            self._queue_messages(messages, reason=f"{provider_name} is not configured.")
            return "queued"

        try:
            for message in messages:
                await self._email_provider.send(message)
        except Exception as exc:
            logger.warning(
                "%s delivery failed; queueing emails to outbox.",
                provider_name,
                exc_info=exc,
            )
            self._queue_messages(messages, reason=f"{provider_name} delivery failed.")
            return "queued"

        return "sent"

    def _build_contact_messages(
        self,
        contact: ContactRequest,
        ai: AIAnalysis,
    ) -> list[EmailMessageData]:
        owner_body = _render_owner_email(contact, ai)
        user_body = _render_user_email(contact)

        return [
            EmailMessageData(
                to=self._settings.contact_owner_email,
                subject=f"New contact request from {contact.name}",
                body=owner_body,
            ),
            EmailMessageData(
                to=contact.email,
                subject="We received your message",
                body=user_body,
            ),
        ]

    def _queue_messages(self, messages: list[EmailMessageData], *, reason: str) -> None:
        for message in messages:
            self._outbox_repository.enqueue(_message_to_outbox_payload(message, reason=reason))


def _render_owner_email(contact: ContactRequest, ai: AIAnalysis) -> str:
    return (
        "New contact submission\n\n"
        f"Name: {contact.name}\n"
        f"Email: {contact.email}\n"
        f"Phone: {contact.phone}\n\n"
        f"Comment:\n{contact.comment}\n\n"
        "AI analysis:\n"
        f"Category: {ai.category}\n"
        f"Sentiment: {ai.sentiment}\n"
        f"Priority: {ai.priority}\n"
        f"Confidence: {ai.confidence}\n"
        f"Fallback used: {ai.fallback_used}\n"
        f"Summary: {ai.summary}\n"
    )


def _render_user_email(contact: ContactRequest) -> str:
    return (
        f"Thank you for your message, {contact.name}.\n\n"
        "I received your request and will reply as soon as possible.\n\n"
        "Your message:\n"
        f"{contact.comment}\n"
    )


def _message_to_outbox_payload(message: EmailMessageData, *, reason: str) -> JsonObject:
    return {
        "to": str(message.to),
        "subject": message.subject,
        "body": message.body,
        "reason": reason,
    }


def _build_email_provider(settings: Settings) -> EmailProvider:
    if settings.email_provider.lower() == "resend":
        return ResendClient(settings)
    return SMTPClient(settings)


def _provider_name(provider: EmailProvider) -> str:
    name = getattr(provider, "name", "SMTP")
    return str(name)
