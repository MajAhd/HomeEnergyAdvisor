# Engineering notes

Companion to the root README: design rationale, production-readiness thinking, and
the AI Tool Usage Log the brief asks for. Written for a reviewer who's already read
the README and wants the "why," not a restatement of the "what."

## Prompt & schema design

`SYSTEM_PROMPT` (`backend/app/llm/prompts.py`) is static and provider-neutral: 
it never mentions a specific home, so the same 182-word block is reused verbatim on
every call - relevant later (see token usage, below). Rules baked into it: ground
every recommendation strictly in the submitted fields ("do not invent facts"),
vary priority with the home's actual profile (old + poorly insulated + gas skews
"high"; new + efficient skews "low"), and return 3-6 items ordered by priority.

The response shape is enforced structurally via Anthropic's `output_config.format`
(JSON schema), not described in prose - asking a model to "reply in JSON" is a
probabilistic ask; a schema constraint is a guarantee. One thing I verified rather
than assumed: Anthropic's structured-output schema subset is stricter than plain
JSON Schema - `maxItems` on an array isn't supported at all, and `minItems` only
accepts 0 or 1. I found this by testing schema variants against the live API
(`400 invalid_request_error` on anything else), not by reading docs first. The 3-6
count is enforced by the prompt instead, since the schema can't express it.

## Reducing LLM token usage & cost

Three concrete levers, in the order I'd actually reach for them:

1. **Right-size `max_tokens`.** It's currently set to 8000 (`anthropic_client.py`)
   - a blank check. A 6-recommendation structured response tops out around
   1000-1200 output tokens in practice. Capping it around 1500 bounds worst-case
   cost and latency per call without touching normal responses; it's a one-line
   change I'm calling out here rather than making silently, since "why 8000" is a
   fair review question.
2. **Prompt-cache the static system prompt.** `SYSTEM_PROMPT` is identical on
   every request, so it's a textbook case for Anthropic's prompt caching: passing
   it as `system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control":
   {"type": "ephemeral"}}]` instead of a plain string lets Anthropic cache those
   ~240 input tokens server-side and bill the cache-read rate on every call after
   the first. Zero risk (same output), and the saving scales with traffic instead
   of being a one-time fix - the right lever to pull before touching prompt
   content itself.
3. **Don't restate the schema in prose.** The response shape is enforced only via
   `output_config.format`, never re-described in `SYSTEM_PROMPT` - a common
   mistake that silently doubles input tokens (once in English, once in the
   schema param) for zero benefit once structured outputs are already doing the
   enforcement.

Beyond token-counting: the biggest single cost lever is model choice, not prompt
micro-optimization. This runs on `claude-haiku-4-5-20251001`, not a larger model - for a
bounded-output extraction task like "turn a home profile into 3-6 JSON
recommendations," the smallest model that reliably follows the schema is usually
a bigger win than shaving tokens off an already-small prompt.

## Caching duplicate advice requests

Advice is generated fresh on every `POST /advice` call
(`services/advice_service.py`) - no persistence, so refreshing the same home's
page re-runs the full LLM call for identical input. Real cost multiplier, zero
user-facing benefit.

Cache key: a hash of the fields that actually feed the prompt - `size_sqm`,
`year_built`, `heating_type`, `insulation_quality`, `occupants` - not `home_id`.
Two different homes with identical profiles should share a cache entry; a hash of
the content is the correct key, `home_id` is an implementation detail of storage.

Storage: for this app's scope (single backend process, no horizontal scaling), an
in-process TTL cache is enough - `functools.lru_cache` or a small dict keyed by
the hash. Behind more than one instance, that breaks (a hit on instance A is
invisible to instance B), so it'd need to move to Redis or the database itself
before this app ever ran with `replicas: 2`.

This same keyed store, built with a per-key lock ("single-flight"), also solves
the concurrent-request problem below - it's the same gap seen from two angles:
repeat callers over time vs. simultaneous callers right now.

## Idempotency & race conditions

Two concrete gaps, both checkable against the current code:

- **`POST /api/homes` has no dedup.** `Home.id` is server-generated
  (`uuid.uuid4()` in `db/models.py`), never client-supplied, so a client retry
  after a dropped response (fetch times out, server actually succeeded) creates a
  second, indistinguishable row. No unique constraint would catch it - two
  genuinely different homes can legitimately share every field.
- **`POST /.../advice` does no request coalescing.** Two tabs (or a double-click)
  hitting the same home's advice endpoint concurrently each reach
  `AnthropicLLMClient.generate_advice()` independently - two LLM calls billed for
  what the user experiences as one action.

Fix I'd reach for: an `Idempotency-Key` header (Stripe's pattern) - the client
generates a UUID once per logical action; the server keeps a short-TTL
`key -> response` store and, on a repeat key, returns the stored response instead
of re-running the handler. One mechanism covers both gaps: on `POST /api/homes` a
repeat key returns the existing home instead of a duplicate; on `POST /.../advice`
a repeat key returns the cached/in-flight result instead of firing a second LLM
call. It's the same key-value shape as the caching design above, just keyed by a
client-supplied token instead of a content hash.

Not built here: idempotency keys earn their cost where retries are likely (flaky
mobile networks, load-balancer failover, multiple backend instances) - none of
which this exercise's environment has, and the brief explicitly scopes out auth
and deployment.

## Logging

One line per request (`app/api/middleware.py`), logged at INFO/WARNING/ERROR by
response status, plus INFO from the service layer for domain events and ERROR
from the exception handlers with the underlying failure reason. Every request
gets an `X-Request-ID` (reused if the caller sent one, generated otherwise),
echoed in the response header and in every log line for that request, so a
client-reported error traces back to its exact server-side lines even with no log
aggregation. Configured centrally (`app/core/logging.py`) so app code and
dependencies share one format; uvicorn's own access log is disabled since our
line already carries the same information plus duration and the request id.

## Assumptions & tradeoffs

- **No auth, migrations, or deployment config** - out of scope per the brief.
  `Base.metadata.create_all()` on startup instead of Alembic; fine for SQLite at
  this size.
- **SQLite over Postgres** - zero setup, no extra Compose service. No
  SQLite-specific logic (`app/db/session.py` swaps dialects via `DATABASE_URL`
  alone), so moving to Postgres is a config change, not a rewrite.

- **Advice isn't cached or persisted** - see "Caching duplicate advice requests"
  above for the design I'd build; not built now to keep the core LLM integration
  the focus of a time-boxed exercise.
- **Frontend TS types are hand-mirrored from the backend's Pydantic schemas**, not
  generated. Duplication is small and static at this size.
- **Minimal styling, scoped CSS per component** - per the brief's "skip elaborate
  styling."
- **Single LLM provider (Anthropic)** - the `LLMClient` interface
  (`app/llm/base.py`) exists specifically so a second provider could be added
  without touching the API layer or services. I prototyped and live-tested a
  multi-provider fallback chain (Anthropic → Gemini → Groq → mock) during
  development, then scoped it back out to match the brief's single-provider ask.

## What I'd improve with more time

- Idempotency keys + the advice cache described above (same mechanism, two call
  sites) - the highest-value addition if this saw real traffic.
- Prompt-cache the system prompt and right-size `max_tokens` (see "Reducing LLM
  token usage" above).
- Generate the frontend's TS types from the backend's OpenAPI schema instead of
  hand-mirroring them.
- An eval set for the advice prompt (a handful of home profiles with expected
  priority ordering) to catch prompt regressions instead of eyeballing output.
- Alembic migrations, Postgres, and basic auth if this went towards production.
- Structured (JSON) logs instead of plain text, if this fed a log aggregator
  rather than a terminal - the current format optimizes for human readability at
  this scale.

## AI Tool Usage Log

**Tools used:** Claude Code (Sonnet 5), using its built-in Anthropic API reference
skill to verify current SDK usage rather than relying on training-data recall.

**AI-assisted:** almost all of the boilerplate and repetitive layers - Pydantic
schemas, SQLAlchemy models, the FastAPI router, the Pinia store, Vue component
templates, and the full backend + frontend test suites.

**I designed/directed:** the overall architecture (the `LLMClient` interface
boundary, service-layer separation from routers, the auto/mock/live config
switch), the prompt's grounding and prioritization rules, the choice to use
structured outputs over prompt-only JSON, and the scope cuts and production
tradeoffs documented above. 

AI wrote the code; the decisions about *what* to build
and *why* were mine, and I read every file it produced before treating it as
done - including re-deriving why each test asserts what it asserts.

**Effective prompts:**

1. *"Design your prompt to produce actionable, prioritized recommendations - base
   every recommendation strictly on the home profile provided, don't invent
   facts, and make priority actually vary with the home's age/insulation/heating
   instead of being generic."* - shaped the system prompt directly, and is
   testable: `test_mock_client.py` asserts an old, poorly-insulated home gets
   `high`-priority items and a new, efficient one gets none.
2. *"Use Anthropic's current structured-outputs API instead of asking the model
   to reply in JSON in the prompt text."* - led to `output_config.format` with an
   explicit JSON schema, eliminating most response-parsing failures by
   construction rather than by retry logic.
3. *"Before writing the LLM client, check the current Anthropic API docs rather
   than assuming - verify the model ID and SDK version."* - caught a real bug
   before it shipped (below).

**One thing AI got wrong that had to be fixed:** the backend's `pyproject.toml`
was initially written with `anthropic = ">=0.40.0,<1.0.0"`, based on a stale prior
about the SDK's version line. `pip index versions anthropic` showed the current
major release is actually `1.3.0` (a breaking rewrite - different HTTP internals,
`httpx2` instead of `httpx`), so the constraint was corrected, re-locked, and
reinstalled before writing the client against it. Smaller version of the same
lesson on the frontend: the initial `ApiError` class used constructor
parameter-property shorthand (`constructor(message: string, public readonly
status: number)`), which failed `vue-tsc` under this project's
`erasableSyntaxOnly` compiler flag - a real compile error, fixed by declaring the
field separately.
