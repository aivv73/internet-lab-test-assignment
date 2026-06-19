from app.core.config import Settings
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricsResponse


class MetricsService:
    """Read aggregate metrics for the metrics API."""

    def __init__(self, settings: Settings) -> None:
        self._repository = MetricsRepository(settings.storage_dir)

    def get_metrics(self) -> MetricsResponse:
        return self._repository.get()
