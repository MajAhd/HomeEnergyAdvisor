# Home Energy Advisor

A small full-stack app: describe your home, get AI-generated, prioritized energy
efficiency recommendations. Built for a take-home engineering exercise.

- **Backend:** FastAPI, SQLAlchemy + SQLite, Poetry
- **Frontend:** Vue 3 (`<script setup>`), TypeScript, Pinia, Vite
- **LLM:** Anthropic Claude, structured JSON outputs, with a
  deterministic rule-based mock fallback when no API key is configured
- **Dev environment:** Docker Compose file

## Architecture at a glance

```
backend/app/
├── api/            FastAPI routers + dependency wiring (homes.py, deps.py)
├── services/        request orchestration (home_service, advice_service)
├── llm/              provider-agnostic LLMClient interface + Anthropic/mock impls
├── db/                SQLAlchemy models, engine/session
├── schemas/         Pydantic request/response models
└── models/enums.py  shared enums (heating type, insulation, priority)

frontend/src/
├── api/client.ts     typed fetch wrapper, ApiError
├── stores/home.ts    Pinia store: orchestrates create-home -> get-advice
├── components/       HomeForm, AdviceList, RecommendationCard
└── types/home.ts     TS types mirroring the backend schemas
```

The backend is layered so each piece is replaceable and independently testable:
routers never touch SQLAlchemy or the LLM directly, they call into `services/`;
`services/` depends on an `LLMClient` **interface** (`app/llm/base.py`), not a
concrete provider, so `AnthropicLLMClient` and `MockLLMClient` are interchangeable
(`app/api/deps.py` picks one based on config, with no other code aware of the
switch).

## Setup

Requires Docker and Docker Compose.

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (interactive docs at `/docs`)

That's it — **no API key is required**. With no `ANTHROPIC_API_KEY` set, the
`/advice` endpoint automatically falls back to a deterministic, rule-based mock
advisor (see `backend/app/llm/mock_client.py`) that produces realistic-looking,
home-specific recommendations, clearly labeled `"source": "mock"` in the response
and in the UI.

### Using the real LLM

Export a key in your shell before starting Compose (never hardcode it into
`docker-compose.yml`, which is committed):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up --build
```

`docker-compose.yml` passes it through via `${ANTHROPIC_API_KEY:-}`. Alternatively,
create a root-level `.env` file (already gitignored) with
`ANTHROPIC_API_KEY=sk-ant-...` — Compose loads that automatically for variable
substitution. This is Compose's own `.env` mechanism, separate from (and not to be
confused with) a Python `.env` loaded by the app itself, which this project
deliberately doesn't use — see Assumptions & Tradeoffs.

Force a specific mode regardless of whether a key is set with `LLM_MODE=mock` or
`LLM_MODE=live` (default `auto`).

Set `LOG_LEVEL` (default `INFO`) to control verbosity, e.g. `LOG_LEVEL=DEBUG`.

### Running without Docker

```bash
# Backend
cd backend
poetry install
LLM_MODE=mock poetry run uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Tests

```bash
# Backend - 42 tests, ~96% coverage
cd backend
poetry run pytest --cov=app --cov-report=term-missing
poetry run ruff check .   # lint
poetry run ruff format .  # format

# Frontend - 19 tests
cd frontend
npm run test
npm run type-check
npm run lint      # eslint (add --fix, or use `npm run lint:fix`)
npm run format    # prettier --write
```

## API

| Method | Endpoint                 | Description                                     |
| ------ | ------------------------ | ----------------------------------------------- |
| POST   | `/api/homes`             | Create a home profile                           |
| GET    | `/api/homes/{id}`        | Retrieve a home profile                         |
| POST   | `/api/homes/{id}/advice` | Generate prioritized energy-saving advice (LLM) |

Errors follow a consistent `{"detail": "..."}` body: `404` for an unknown home,
`422` for validation failures (FastAPI/Pydantic default), `502` when the LLM
provider fails or returns something we can't parse (the LLM is an external
dependency, so this is modeled as a gateway error, not our own bug).
