from collections.abc import Mapping
from typing import cast

import httpx
import pytest

from app.core.config import Settings
from app.handlers.ai_client import AIProviderError, OpenAICompatibleAIClient
from app.repositories.json_file import JsonObject
from app.schemas.contact import ContactRequest
from app.services.ai_service import AIProvider, AIService


def contact_request() -> ContactRequest:
    return ContactRequest.model_validate(
        {
            "name": "Ivan Petrov",
            "email": "ivan@example.com",
            "phone": "+7 999 123-45-67",
            "comment": "Hello! I want to discuss backend API development for my project.",
        }
    )


class SuccessfulProvider:
    async def analyze_contact(self, _contact: ContactRequest) -> JsonObject:
        return {
            "category": "project_inquiry",
            "sentiment": "positive",
            "summary": "User wants to discuss backend API development.",
            "priority": "normal",
            "confidence": 0.91,
        }


class FailingProvider:
    async def analyze_contact(self, _contact: ContactRequest) -> JsonObject:
        raise AIProviderError("provider unavailable")


class FakeHttpClient:
    def __init__(self) -> None:
        self.last_request: JsonObject | None = None

    async def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: JsonObject,
    ) -> httpx.Response:
        self.last_request = {"url": url, "headers": headers, "json": json}
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"category":"job_offer","sentiment":"neutral",'
                                '"summary":"User has a job offer.","priority":"high",'
                                '"confidence":0.8}'
                            )
                        }
                    }
                ]
            },
        )


@pytest.mark.asyncio
async def test_ai_service_returns_fallback_without_api_key() -> None:
    service = AIService(Settings(ai_api_key=None))

    analysis = await service.analyze(contact_request())

    assert analysis.category == "unknown"
    assert analysis.fallback_used is True


@pytest.mark.asyncio
async def test_ai_service_returns_provider_analysis() -> None:
    service = AIService(
        Settings(ai_api_key="test-key"),
        provider=cast(AIProvider, SuccessfulProvider()),
    )

    analysis = await service.analyze(contact_request())

    assert analysis.category == "project_inquiry"
    assert analysis.sentiment == "positive"
    assert analysis.confidence == 0.91
    assert analysis.fallback_used is False


@pytest.mark.asyncio
async def test_ai_service_falls_back_when_provider_fails() -> None:
    service = AIService(
        Settings(ai_api_key="test-key"),
        provider=cast(AIProvider, FailingProvider()),
    )

    analysis = await service.analyze(contact_request())

    assert analysis.category == "unknown"
    assert analysis.fallback_used is True


@pytest.mark.asyncio
async def test_ai_service_normalizes_unexpected_provider_values() -> None:
    class UnexpectedProvider:
        async def analyze_contact(self, _contact: ContactRequest) -> JsonObject:
            return {
                "category": "unexpected",
                "sentiment": "unexpected",
                "summary": "Summary",
                "priority": "urgent",
                "confidence": 2.5,
            }

    service = AIService(
        Settings(ai_api_key="test-key"),
        provider=cast(AIProvider, UnexpectedProvider()),
    )

    analysis = await service.analyze(contact_request())
    assert analysis.category == "unknown"
    assert analysis.sentiment == "unknown"
    assert analysis.priority == "normal"
    assert analysis.confidence == 1.0


@pytest.mark.asyncio
async def test_openai_compatible_client_uses_configured_model() -> None:
    http_client = FakeHttpClient()
    settings = Settings(ai_api_key="test-key", ai_model="gpt-5.4-nano")
    client = OpenAICompatibleAIClient(settings, http_client=http_client)

    analysis = await client.analyze_contact(contact_request())

    assert analysis["category"] == "job_offer"
    assert http_client.last_request is not None
    assert http_client.last_request["url"] == "https://api.openai.com/v1/chat/completions"
    assert http_client.last_request["json"]["model"] == "gpt-5.4-nano"
