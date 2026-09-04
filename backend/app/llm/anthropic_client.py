import json
import logging
import time

import anthropic
from pydantic import ValidationError

from app.db.models import Home
from app.exceptions import LLMError, LLMResponseParsingError
from app.llm.base import LLMAdviceResult, LLMClient
from app.llm.prompts import RECOMMENDATION_JSON_SCHEMA, SYSTEM_PROMPT, build_user_prompt
from app.schemas.home import Recommendation

logger = logging.getLogger(__name__)


class AnthropicLLMClient(LLMClient):
    """Real LLM-backed advice generator, using the Anthropic Messages API.

    Uses structured outputs (`output_config.format`) rather than asking the model to
    "reply in JSON" in the prompt: it guarantees the response is valid JSON matching
    our schema instead of merely making it likely, which removes an entire class of
    parsing failures.
    """

    PROVIDER = "Anthropic"

    def __init__(self, api_key: str, model: str, timeout_seconds: float):
        self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds)
        self._model = model

    def generate_advice(self, home: Home) -> LLMAdviceResult:
        """Log the request lifecycle (start, duration, outcome) around the actual
        API call and parsing, which stay factored out in `_call` / `_parse` - keeps
        the exception-mapping and response-parsing logic free of logging concerns.
        """
        logger.info(
            "%s: requesting advice for home %s (model=%s)", self.PROVIDER, home.id, self._model
        )
        start = time.perf_counter()
        try:
            response = self._call(home)
            result = self._parse(response)
        except (LLMError, LLMResponseParsingError) as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.warning(
                "%s: request failed for home %s after %.0fms - %s",
                self.PROVIDER,
                home.id,
                duration_ms,
                exc,
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s: request succeeded for home %s in %.0fms (%d recommendation(s))",
            self.PROVIDER,
            home.id,
            duration_ms,
            len(result.recommendations),
        )
        return result

    def _call(self, home: Home) -> anthropic.types.Message:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=8000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_user_prompt(home)}],
                output_config={
                    "format": {"type": "json_schema", "schema": RECOMMENDATION_JSON_SCHEMA},
                },
            )
        except anthropic.AuthenticationError as exc:
            raise LLMError("LLM provider rejected our API key") from exc
        except anthropic.PermissionDeniedError as exc:
            raise LLMError("LLM API key lacks required permissions") from exc
        except anthropic.RateLimitError as exc:
            raise LLMError("LLM provider rate limit exceeded, please retry shortly") from exc
        except anthropic.BadRequestError as exc:
            raise LLMError(f"LLM provider rejected the request: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise LLMError("Could not reach the LLM provider") from exc
        except anthropic.APIStatusError as exc:
            raise LLMError(f"LLM provider error (status {exc.status_code})") from exc

        if response.stop_reason == "refusal":
            raise LLMResponseParsingError("LLM declined to generate advice for this request")

        return response

    def _parse(self, response: anthropic.types.Message) -> LLMAdviceResult:
        text = next((block.text for block in response.content if block.type == "text"), None)
        if text is None:
            raise LLMResponseParsingError("LLM response contained no text content")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("LLM response was not valid JSON: %s", text[:500])
            raise LLMResponseParsingError("LLM response was not valid JSON") from exc

        try:
            recommendations = [Recommendation(**item) for item in data["recommendations"]]
            summary = data["summary"]
        except (ValidationError, KeyError, TypeError) as exc:
            logger.warning("LLM response did not match expected schema: %s", data)
            raise LLMResponseParsingError("LLM response did not match the expected schema") from exc

        return LLMAdviceResult(summary=summary, recommendations=recommendations)
