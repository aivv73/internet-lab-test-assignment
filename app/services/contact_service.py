import logging
from datetime import UTC, datetime
from uuid import uuid4

from app.core.config import Settings
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.rate_limit_repository import RateLimitRepository
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.contact import ContactRequest, ContactResponse
from app.services.ai_service import AIService
from app.services.email_service import EmailService
from app.services.rate_limit_service import RateLimitService

logger = logging.getLogger("app.contact")


class ContactService:
    """Orchestrate the full contact submission workflow."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._submission_repository = SubmissionRepository(settings.storage_dir)
        self._metrics_repository = MetricsRepository(settings.storage_dir)
        self._rate_limit_service = RateLimitService(
            RateLimitRepository(settings.storage_dir),
            settings,
        )
        self._ai_service = AIService(settings)
        self._email_service = EmailService(settings, OutboxRepository(settings.storage_dir))

    async def submit(self, contact: ContactRequest, *, client_ip: str) -> ContactResponse:
        """Run validation-adjacent business workflow after Pydantic validation."""
        self._rate_limit_service.check_and_increment(
            ip_address=client_ip,
            email=str(contact.email),
        )

        ai = await self._ai_service.analyze(contact)
        submission_id = str(uuid4())
        created_at = datetime.now(UTC)

        self._submission_repository.save(
            submission_id,
            {
                "id": submission_id,
                "created_at": created_at.isoformat(),
                "client_ip": client_ip,
                "contact": contact.model_dump(mode="json"),
                "ai": ai.model_dump(mode="json"),
                "email_delivery": None,
            },
        )

        email_delivery = await self._email_service.send_contact_emails(contact, ai)

        self._submission_repository.save(
            submission_id,
            {
                "id": submission_id,
                "created_at": created_at.isoformat(),
                "client_ip": client_ip,
                "contact": contact.model_dump(mode="json"),
                "ai": ai.model_dump(mode="json"),
                "email_delivery": email_delivery,
            },
        )
        self._metrics_repository.record_submission(ai, email_delivery)

        logger.info(
            "Accepted contact submission id=%s client_ip=%s email_delivery=%s ai_fallback=%s",
            submission_id,
            client_ip,
            email_delivery,
            ai.fallback_used,
        )

        return ContactResponse(
            id=submission_id,
            email_delivery=email_delivery,
            ai=ai,
            created_at=created_at,
        )
