import json
from collections.abc import Mapping
from typing import Protocol

import httpx

from app.core.config import Settings
from app.repositories.json_file import JsonObject
from app.schemas.contact import ContactRequest


class AIProviderError(Exception):
    """Raised when the AI provider cannot return a usable response."""


class AsyncHttpClient(Protocol):
    async def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: JsonObject,
    ) -> httpx.Response: ...


class OpenAICompatibleAIClient:
    """OpenAI-compatible chat completions client for contact analysis."""

    def __init__(self, settings: Settings, http_client: AsyncHttpClient | None = None) -> None:
        self._settings = settings
        self._http_client = http_client

    async def analyze_contact(self, contact: ContactRequest) -> JsonObject:
        if not self._settings.ai_api_key:
            raise AIProviderError("AI_API_KEY is not configured.")

        response = await self._post_chat_completion(contact)
        try:
            response.raise_for_status()
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise AIProviderError("AI provider returned an invalid response.") from exc

        return _parse_json_content(str(content))

    async def _post_chat_completion(self, contact: ContactRequest) -> httpx.Response:
        url = f"{self._settings.ai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._settings.ai_api_key}",
            "Content-Type": "application/json",
        }
        body = _build_request_body(contact, self._settings.ai_model)

        if self._http_client is not None:
            return await self._http_client.post(url, headers=headers, json=body)

        async with httpx.AsyncClient(timeout=self._settings.ai_timeout_seconds) as client:
            return await client.post(url, headers=headers, json=body)


def _build_request_body(contact: ContactRequest, model: str) -> JsonObject:
    return {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You classify developer landing contact form submissions. "
                    "Return only valid JSON with keys: category, sentiment, summary, "
                    "priority, confidence. Allowed categories: project_inquiry, job_offer, "
                    "support, spam, other. Allowed sentiments: positive, neutral, negative. "
                    "Allowed priorities: low, normal, high. Confidence must be 0..1."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "name": contact.name,
                        "email": str(contact.email),
                        "phone": contact.phone,
                        "comment": contact.comment,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
    }


def _parse_json_content(content: str) -> JsonObject:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = stripped.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise AIProviderError("AI provider returned non-JSON content.") from exc

    if not isinstance(parsed, dict):
        raise AIProviderError("AI provider JSON content must be an object.")

    return parsed
