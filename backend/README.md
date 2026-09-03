# Backend

FastAPI service for the Home Energy Advisor. For setup via Docker, assumptions,
API design notes, and the AI usage log, see the [root README](../README.MD).

## Run

```bash
poetry install
make run
```

Runs on `http://localhost:8000`. Docs at `/docs`. No `ANTHROPIC_API_KEY` needed —
`LLM_MODE=mock` (or no key at all, in `auto` mode) uses the deterministic mock advisor.

## Commands

```bash
make help         # list all targets
make run          # uvicorn --reload, mock LLM, no Docker needed
make test          # pytest --cov=app --cov-report=term-missing
make lint          # ruff check .
make lint-fix      # ruff check . --fix
make format        # ruff format .
```

## Layout

```
app/
  api/        routes, request-logging middleware, DI (llm client, db session)
  core/       config (env vars), logging setup
  db/         SQLAlchemy models + session
  llm/        LLMClient interface, Anthropic + mock implementations, prompts
  schemas/    Pydantic request/response models
  services/   business logic, called from routes
```

Env vars: `DATABASE_URL`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `LLM_MODE`
(`auto`/`mock`/`live`), `LOG_LEVEL` — see `app/core/config.py` for defaults.
