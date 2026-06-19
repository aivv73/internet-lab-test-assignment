from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings


async def verify_metrics_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """Protect metrics only when METRICS_API_KEY is configured."""
    if not settings.metrics_api_key:
        return

    if x_api_key != settings.metrics_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing metrics API key.",
        )
