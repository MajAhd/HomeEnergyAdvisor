from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # -- General --
    app_name: str = "Home Energy Advisor API"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    log_level: str = "INFO"

    # -- Database --
    # File-based SQLite by default so state survives container restarts when the
    # /data volume is mounted (see docker-compose.yml). Swap for Postgres by setting
    # DATABASE_URL - the code has no SQLite-specific assumptions.
    database_url: str = "sqlite:///./data/home_energy_advisor.db"

    # -- LLM integration --
    # No key -> we fall back to the deterministic mock client automatically, so the
    # app runs out of the box without credentials (see app/api/deps.py).
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5-20251001"
    # Explicit override: "auto" (default) picks mock iff no API key is configured,
    # "mock" and "live" force one or the other regardless of the key. A Literal
    # (rather than a plain str) so a typo'd or unrecognized value fails fast at
    # startup instead of silently falling through to "auto".
    llm_mode: Literal["auto", "mock", "live"] = "auto"
    llm_timeout_seconds: float = 30.0


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance - env vars are read once per process."""
    return Settings()
