# Development plan

Source brief: `doc/Take-home_ Senior Full Stack Engineer Dec 2025.pdf`:

build a "Home Energy Advisor": a form to describe a home, an LLM call that turns it into prioritized energy-saving recommendations, and a UI to show them. Built backend-first so the
frontend has a stable API contract to build against.

## 1. Backend - REST API (FastAPI)

- [x] 1.1 Intial and setup Backend - Poetry, Dockerfile, docker-compose service, pytest/ruff config
- [x] 1.2 Data model - `Home` SQLAlchemy model, SQLite by default (swappable via `DATABASE_URL`)
- [x] 1.3 Schemas - `HomeCreate` / `HomeRead` / `Recommendation` / `AdviceResponse` (Pydantic validation: ranges, enums, no-future-year)
- [x] 1.4 design required Endpoints
- [x] 1.5 LLM integration - `LLMClient` interface, `AnthropicLLMClient` (structured outputs / JSON schema) with a deterministic `MockLLMClient` fallback when no API key is set; prompt grounded in only the submitted fields
- [x] 1.6 Error handling - domain exceptions (`HomeNotFoundError`, `LLMError`, `LLMResponseParsingError`) mapped to HTTP responses (404 / 422 / 502) via FastAPI exception handlers
- [x] 1.7 Logging - Htttp logger (method, path, status, duration, request id) plus INFO/ERROR logs from the service layer
- [x] 1.8 Tests - pytest + coverage (~97%), including the LLM failure/parsing paths and the logging middleware
- [x] 1.9 `Makefile` Lint/format/DX - ruff, (`make run` / `test` / `lint` / `format`)

## 2. Frontend - Vue 3 + TypeScript (Vite)

- [x] 2.1 Intial and setup Frontend - Vite + TypeScript + Pinia
- [x] 2.2 Types mirroring the backend's Pydantic schemas
- [x] 2.3 API client - typed `fetch` wrapper, maps backend error responses to a typed `ApiError`
- [x] 2.4 Pinia store - home profile + advice state, loading/error flags
- [x] 2.5 Components - `HomeForm` (input), `AdviceList` / `RecommendationCard` (results)
- [x] 2.6 `App.vue` - wires form → store → results
- [x] 2.7 Tests - Vitest + Vue Test Utils
- [x] 2.8 Lint/format - ESLint (flat config) + Prettier

## 3. Developer experience

- [x] 3.1 `docker-compose.yml` - one command (`docker compose up`) runs both stacks, no API key required (mock LLM fallback)
- [x] 3.2 READMEs - root (setup, API) + a short one per stack; deeper design notes,
      assumptions/tradeoffs, and the AI Tool Usage Log live in `doc/dev.md`
- [x] 3.3 AI Tool Usage Log - documented in `doc/dev.md` per the brief's deliverables
- [x] 3.4 AAA (Arrange-Act-Assert) testing style - backend test suite only

## Deliverables checklist (per the brief)

- [x] Code repository with setup instructions
- [x] Assumptions / tradeoffs documented
- [x] AI Tool Usage Log
- [x] Mocked LLM responses supported (`LLM_MODE=mock`, also the default with no API key) alongside the real Anthropic integration
