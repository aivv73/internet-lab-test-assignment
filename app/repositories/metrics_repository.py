from pathlib import Path

from app.repositories.json_file import JsonFileRepository, JsonObject
from app.schemas.ai import AIAnalysis
from app.schemas.contact import EmailDeliveryStatus
from app.schemas.metrics import MetricsResponse


class MetricsRepository:
    """Persist aggregate contact metrics in a single JSON file."""

    def __init__(self, storage_dir: Path) -> None:
        self._json = JsonFileRepository(storage_dir)
        self._path = storage_dir / "metrics.json"

    def get(self) -> MetricsResponse:
        data = self._json.read_json(self._path, default=_default_metrics())
        return MetricsResponse.model_validate(data)

    def save(self, metrics: MetricsResponse) -> None:
        self._json.write_json(self._path, metrics.model_dump())

    def record_submission(
        self,
        ai: AIAnalysis,
        email_delivery: EmailDeliveryStatus,
    ) -> MetricsResponse:
        metrics = self.get()
        metrics.total_submissions += 1
        metrics.by_category[ai.category] = metrics.by_category.get(ai.category, 0) + 1
        metrics.by_sentiment[ai.sentiment] = metrics.by_sentiment.get(ai.sentiment, 0) + 1
        metrics.email_delivery[email_delivery] = metrics.email_delivery.get(email_delivery, 0) + 1
        if ai.fallback_used:
            metrics.ai_fallbacks += 1
        self.save(metrics)
        return metrics


def _default_metrics() -> JsonObject:
    return MetricsResponse().model_dump()
