import logging
from typing import Protocol

from pydantic import ValidationError

from app.core.config import Settings
from app.handlers.ai_client import OpenAICompatibleAIClient
from app.repositories.json_file import JsonObject
from app.schemas.ai import AIAnalysis, fallback_ai_analysis
from app.schemas.contact import ContactRequest

logger = logging.getLogger("app.ai")


class AIProvider(Protocol):
    async def analyze_contact(self, contact: ContactRequest) -> JsonObject: ...


class AIService:
    """Analyze contact submissions with graceful fallback."""

    def __init__(self, settings: Settings, provider: AIProvider | None = None) -> None:
        self._settings = settings
        self._provider = provider

    async def analyze(self, contact: ContactRequest) -> AIAnalysis:
        if not self._settings.ai_api_key and self._provider is None:
            return fallback_ai_analysis()

        provider = self._provider or OpenAICompatibleAIClient(self._settings)
        try:
            raw_analysis = await provider.analyze_contact(contact)
            return _normalize_ai_analysis(raw_analysis)
        except Exception as exc:
            logger.warning("AI analysis failed; using fallback.", exc_info=exc)
            return fallback_ai_analysis()


def _normalize_ai_analysis(raw: JsonObject) -> AIAnalysis:
    normalized = {
        "category": _normalize_choice(
            raw.get("category"),
            allowed={"project_inquiry", "job_offer", "support", "spam", "other", "unknown"},
            default="unknown",
        ),
        "sentiment": _normalize_choice(
            raw.get("sentiment"),
            allowed={"positive", "neutral", "negative", "unknown"},
            default="unknown",
        ),
        "summary": str(raw.get("summary") or "AI analysis unavailable")[:500],
        "priority": _normalize_choice(
            raw.get("priority"),
            allowed={"low", "normal", "high"},
            default="normal",
        ),
        "confidence": _normalize_confidence(raw.get("confidence")),
        "fallback_used": False,
    }

    try:
        return AIAnalysis.model_validate(normalized)
    except ValidationError:
        return fallback_ai_analysis()


def _normalize_choice(value: object, *, allowed: set[str], default: str) -> str:
    if not isinstance(value, str):
        return default
    normalized = value.strip().lower()
    return normalized if normalized in allowed else default


def _normalize_confidence(value: object) -> float:
    if not isinstance(value, int | float):
        return 0.0
    return min(max(float(value), 0.0), 1.0)
