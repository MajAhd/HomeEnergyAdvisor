import json
from dataclasses import dataclass, field
from unittest.mock import MagicMock

import anthropic
import httpx
import pytest

from app.db.models import Home
from app.exceptions import LLMError, LLMResponseParsingError
from app.llm.anthropic_client import AnthropicLLMClient
from app.models.enums import HeatingType, InsulationQuality


@dataclass
class FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class FakeMessage:
    content: list = field(default_factory=list)
    stop_reason: str = "end_turn"


def _home() -> Home:
    return Home(
        id="test-id",
        size_sqm=100.0,
        year_built=1990,
        heating_type=HeatingType.GAS,
        insulation_quality=InsulationQuality.POOR,
        occupants=4,
    )


def _client_with_fake_response(response) -> AnthropicLLMClient:
    client = AnthropicLLMClient(api_key="test-key", model="claude-opus-5", timeout_seconds=5)
    client._client = MagicMock()
    client._client.messages.create.return_value = response
    return client


VALID_PAYLOAD = {
    "summary": "A drafty older home with room for improvement.",
    "recommendations": [
        {
            "title": "Add loft insulation",
            "description": "Cuts heat loss substantially.",
            "priority": "high",
            "category": "insulation",
            "estimated_annual_savings_eur": 300.0,
        },
        {
            "title": "Service the boiler",
            "description": "Keeps it running efficiently.",
            "priority": "low",
            "category": "heating",
            "estimated_annual_savings_eur": None,
        },
    ],
}


def test_parses_valid_structured_response() -> None:
    # Arrange
    response = FakeMessage(content=[FakeTextBlock(text=json.dumps(VALID_PAYLOAD))])
    client = _client_with_fake_response(response)

    # Act
    result = client.generate_advice(_home())

    # Assert
    assert result.summary == VALID_PAYLOAD["summary"]
    assert len(result.recommendations) == 2
    assert result.recommendations[0].priority == "high"


def test_raises_parsing_error_on_malformed_json() -> None:
    # Arrange
    response = FakeMessage(content=[FakeTextBlock(text="not json at all")])
    client = _client_with_fake_response(response)

    # Act & Assert
    with pytest.raises(LLMResponseParsingError):
        client.generate_advice(_home())


def test_raises_parsing_error_when_schema_fields_missing() -> None:
    # Arrange
    response = FakeMessage(content=[FakeTextBlock(text=json.dumps({"summary": "ok"}))])
    client = _client_with_fake_response(response)

    # Act & Assert
    with pytest.raises(LLMResponseParsingError):
        client.generate_advice(_home())


def test_raises_parsing_error_on_refusal_stop_reason() -> None:
    # Arrange
    response = FakeMessage(content=[], stop_reason="refusal")
    client = _client_with_fake_response(response)

    # Act & Assert
    with pytest.raises(LLMResponseParsingError):
        client.generate_advice(_home())


def test_raises_parsing_error_when_no_text_block_present() -> None:
    # Arrange
    response = FakeMessage(content=[])
    client = _client_with_fake_response(response)

    # Act & Assert
    with pytest.raises(LLMResponseParsingError):
        client.generate_advice(_home())


def _fake_request() -> httpx.Request:
    return httpx.Request("POST", "https://api.anthropic.com/v1/messages")


def test_wraps_authentication_error_as_llm_error() -> None:
    # Arrange
    client = AnthropicLLMClient(api_key="bad-key", model="claude-opus-5", timeout_seconds=5)
    client._client = MagicMock()
    client._client.messages.create.side_effect = anthropic.AuthenticationError(
        message="invalid x-api-key",
        response=httpx.Response(401, request=_fake_request()),
        body=None,
    )

    # Act & Assert
    with pytest.raises(LLMError):
        client.generate_advice(_home())


def test_wraps_rate_limit_error_as_llm_error() -> None:
    # Arrange
    client = AnthropicLLMClient(api_key="test-key", model="claude-opus-5", timeout_seconds=5)
    client._client = MagicMock()
    client._client.messages.create.side_effect = anthropic.RateLimitError(
        message="rate limited",
        response=httpx.Response(429, request=_fake_request()),
        body=None,
    )

    # Act & Assert
    with pytest.raises(LLMError):
        client.generate_advice(_home())


def test_wraps_connection_error_as_llm_error() -> None:
    # Arrange
    client = AnthropicLLMClient(api_key="test-key", model="claude-opus-5", timeout_seconds=5)
    client._client = MagicMock()
    client._client.messages.create.side_effect = anthropic.APIConnectionError(
        request=_fake_request()
    )

    # Act & Assert
    with pytest.raises(LLMError):
        client.generate_advice(_home())
