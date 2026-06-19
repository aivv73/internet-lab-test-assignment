from fastapi import APIRouter, Depends

from app.core.security import verify_metrics_api_key
from app.schemas.metrics import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse, dependencies=[Depends(verify_metrics_api_key)])
async def get_metrics() -> MetricsResponse:
    """Return aggregate contact metrics.

    This returns empty demo metrics until the metrics repository/service is implemented.
    """
    return MetricsResponse()
