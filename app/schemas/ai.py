from typing import Literal

from pydantic import BaseModel, Field

ContactCategory = Literal[
    "project_inquiry",
    "job_offer",
    "support",
    "spam",
    "other",
    "unknown",
]
Sentiment = Literal["positive", "neutral", "negative", "unknown"]
Priority = Literal["low", "normal", "high"]


class AIAnalysis(BaseModel):
    """AI enrichment returned for a contact submission."""

    category: ContactCategory = Field(
        description="AI-classified request category.",
        examples=["project_inquiry"],
    )
    sentiment: Sentiment = Field(
        description="AI-estimated sentiment of the user's comment.",
        examples=["positive"],
    )
    summary: str = Field(
        min_length=1,
        max_length=500,
        description="Short owner-facing summary of the contact request.",
        examples=["User wants to discuss backend API development for a new project."],
    )
    priority: Priority = Field(
        description="Suggested handling priority.",
        examples=["normal"],
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="AI confidence score between 0 and 1.",
        examples=[0.87],
    )
    fallback_used: bool = Field(
        default=False,
        description="True when deterministic fallback was used instead of provider AI.",
    )


def fallback_ai_analysis() -> AIAnalysis:
    """Return the deterministic AI fallback defined by ADR-0002."""
    return AIAnalysis(
        category="unknown",
        sentiment="unknown",
        summary="AI analysis unavailable",
        priority="normal",
        confidence=0.0,
        fallback_used=True,
    )
