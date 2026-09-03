import pytest

from app.api.deps import advice_source_label, get_llm_client
from app.core.config import Settings
from app.llm.anthropic_client import AnthropicLLMClient
from app.llm.mock_client import MockLLMClient


@pytest.fixture(autouse=True)
def _clear_cache():
    get_llm_client.cache_clear()
    yield
    get_llm_client.cache_clear()


def test_auto_mode_uses_mock_when_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.api.deps.get_settings",
        lambda: Settings(llm_mode="auto", anthropic_api_key=None),
    )

    client = get_llm_client()

    assert isinstance(client, MockLLMClient)
    assert advice_source_label(client) == "mock"


def test_auto_mode_uses_live_client_when_api_key_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.api.deps.get_settings",
        lambda: Settings(llm_mode="auto", anthropic_api_key="sk-test"),
    )

    client = get_llm_client()

    assert isinstance(client, AnthropicLLMClient)
    assert advice_source_label(client) == "llm"


def test_forced_mock_mode_ignores_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.api.deps.get_settings",
        lambda: Settings(llm_mode="mock", anthropic_api_key="sk-test"),
    )

    assert isinstance(get_llm_client(), MockLLMClient)


def test_forced_live_mode_without_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.api.deps.get_settings",
        lambda: Settings(llm_mode="live", anthropic_api_key=None),
    )

    with pytest.raises(RuntimeError):
        get_llm_client()
