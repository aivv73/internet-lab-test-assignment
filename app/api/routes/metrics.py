from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.security import verify_metrics_api_key
from app.schemas.metrics import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse, dependencies=[Depends(verify_metrics_api_key)])
async def get_metrics(settings: Annotated[Settings, Depends(get_settings)]) -> MetricsResponse:
    """Return aggregate contact metrics."""
    return MetricsService(settings).get_metrics()
