import logging
from functools import lru_cache

from app.core.config import get_settings
from app.llm.anthropic_client import AnthropicLLMClient
from app.llm.base import LLMClient
from app.llm.mock_client import MockLLMClient

logger = logging.getLogger(__name__)


@lru_cache
def get_llm_client() -> LLMClient:
    """Build the LLM client once per process based on config.

    LLM_MODE=auto (default) uses the real Anthropic client when ANTHROPIC_API_KEY is
    set, and falls back to the deterministic mock otherwise - this is what lets the
    app run out of the box with `docker compose up`, no credentials required, while
    still exercising the real integration whenever a key is provided.
    """
    settings = get_settings()

    if settings.llm_mode == "mock":
        logger.info("LLM_MODE=mock: using MockLLMClient")
        return MockLLMClient()
    if settings.llm_mode == "live":
        if not settings.anthropic_api_key:
            raise RuntimeError("LLM_MODE=live requires ANTHROPIC_API_KEY to be set")
        logger.info("LLM_MODE=live: using AnthropicLLMClient (model=%s)", settings.anthropic_model)
        return AnthropicLLMClient(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    # auto
    if settings.anthropic_api_key:
        logger.info("LLM_MODE=auto: ANTHROPIC_API_KEY set, using AnthropicLLMClient")
        return AnthropicLLMClient(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    logger.info("LLM_MODE=auto: no ANTHROPIC_API_KEY set, using MockLLMClient")
    return MockLLMClient()


def advice_source_label(llm_client: LLMClient) -> str:
    return "mock" if isinstance(llm_client, MockLLMClient) else "llm"
