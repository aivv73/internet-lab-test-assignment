from collections.abc import Mapping
from typing import Protocol

import httpx

from app.core.config import Settings
from app.repositories.json_file import JsonObject
from app.schemas.email import EmailMessageData


class ResendDeliveryError(Exception):
    """Raised when Resend delivery fails or is not configured."""


class AsyncHttpClient(Protocol):
    async def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: JsonObject,
    ) -> httpx.Response: ...


class ResendClient:
    """Small Resend HTTP API client for transactional email."""

    name = "Resend"

    def __init__(self, settings: Settings, http_client: AsyncHttpClient | None = None) -> None:
        self._settings = settings
        self._http_client = http_client

    @property
    def is_configured(self) -> bool:
        return bool(self._settings.resend_api_key and self._settings.email_from)

    async def send(self, message: EmailMessageData) -> None:
        if not self.is_configured or self._settings.resend_api_key is None:
            raise ResendDeliveryError("Resend is not configured.")

        url = f"{self._settings.resend_base_url.rstrip('/')}/emails"
        headers = {
            "Authorization": f"Bearer {self._settings.resend_api_key}",
            "Content-Type": "application/json",
        }
        body: JsonObject = {
            "from": self._settings.email_from,
            "to": [str(message.to)],
            "subject": message.subject,
            "text": message.body,
        }

        try:
            response = await self._post(url, headers=headers, json=body)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ResendDeliveryError("Resend delivery failed.") from exc

    async def _post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: JsonObject,
    ) -> httpx.Response:
        if self._http_client is not None:
            return await self._http_client.post(url, headers=headers, json=json)

        async with httpx.AsyncClient(timeout=self._settings.ai_timeout_seconds) as client:
            return await client.post(url, headers=headers, json=json)
