from functools import lru_cache

from app.core.config import Settings, get_settings
from app.llm.anthropic_client import AnthropicLLMClient
from app.llm.base import LLMClient
from app.llm.mock_client import MockLLMClient


def _anthropic_client(settings: Settings, api_key: str) -> AnthropicLLMClient:
    return AnthropicLLMClient(
        api_key=api_key,
        model=settings.anthropic_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )


@lru_cache
def get_llm_client() -> LLMClient:
    """Build the LLM client once per process based on config.

    LLM_MODE=auto (default) uses the real Anthropic client when ANTHROPIC_API_KEY is
    set, and falls back to the deterministic mock otherwise
    """
    settings = get_settings()

    if settings.llm_mode == "mock":
        return MockLLMClient()
    if settings.llm_mode == "live":
        if not settings.anthropic_api_key:
            raise RuntimeError("LLM_MODE=live requires ANTHROPIC_API_KEY to be set")
        return _anthropic_client(settings, settings.anthropic_api_key)

    # auto
    if settings.anthropic_api_key:
        return _anthropic_client(settings, settings.anthropic_api_key)
    return MockLLMClient()


def advice_source_label(llm_client: LLMClient) -> str:
    return "mock" if isinstance(llm_client, MockLLMClient) else "llm"
