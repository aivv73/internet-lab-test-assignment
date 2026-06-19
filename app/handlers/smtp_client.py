from email.message import EmailMessage

import aiosmtplib

from app.core.config import Settings
from app.schemas.email import EmailMessageData


class SMTPDeliveryError(Exception):
    """Raised when SMTP delivery fails or is not configured."""


class SMTPClient:
    """Small async SMTP client wrapper."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def is_configured(self) -> bool:
        return bool(self._settings.smtp_host and self._settings.email_from)

    async def send(self, message: EmailMessageData) -> None:
        if not self.is_configured or self._settings.smtp_host is None:
            raise SMTPDeliveryError("SMTP is not configured.")

        email_message = EmailMessage()
        email_message["From"] = self._settings.email_from
        email_message["To"] = str(message.to)
        email_message["Subject"] = message.subject
        email_message.set_content(message.body)

        try:
            await aiosmtplib.send(
                email_message,
                hostname=self._settings.smtp_host,
                port=self._settings.smtp_port,
                username=self._settings.smtp_username,
                password=self._settings.smtp_password,
                start_tls=self._settings.smtp_use_tls,
            )
        except aiosmtplib.SMTPException as exc:
            raise SMTPDeliveryError("SMTP delivery failed.") from exc
