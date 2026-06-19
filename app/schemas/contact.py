from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.ai import AIAnalysis

EmailDeliveryStatus = Literal["sent", "queued"]
ContactSubmissionStatus = Literal["accepted"]


class ContactRequest(BaseModel):
    """Payload accepted by POST /api/contact."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(
        min_length=2,
        max_length=100,
        description="Visitor name.",
        examples=["Ivan Petrov"],
    )
    email: EmailStr = Field(
        description="Visitor email address.",
        examples=["ivan@example.com"],
    )
    phone: str = Field(
        min_length=7,
        max_length=32,
        pattern=r"^[0-9+\s().-]+$",
        description="Visitor phone number. Allows digits, spaces, +, -, parentheses and dots.",
        examples=["+7 999 123-45-67"],
    )
    comment: str = Field(
        min_length=10,
        max_length=2000,
        description="Contact request message.",
        examples=["Hello! I want to discuss backend API development for my project."],
    )


class ContactResponse(BaseModel):
    """Successful response returned by POST /api/contact."""

    id: str = Field(description="Server-generated contact submission id.", examples=["01JABCD123"])
    status: ContactSubmissionStatus = Field(default="accepted")
    email_delivery: EmailDeliveryStatus = Field(
        description="Whether emails were sent via SMTP or queued to file outbox.",
        examples=["queued"],
    )
    ai: AIAnalysis = Field(description="AI analysis included for demo transparency.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when the submission was accepted.",
    )
