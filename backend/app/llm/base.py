from abc import ABC, abstractmethod

from app.db.models import Home
from app.schemas.home import Recommendation


class LLMAdviceResult:
    """Provider-agnostic result of an advice generation call."""

    def __init__(self, summary: str, recommendations: list[Recommendation]):
        self.summary = summary
        self.recommendations = recommendations


class LLMClient(ABC):
    """Interface every advice-generating backend (real or mock) must implement."""

    @abstractmethod
    def generate_advice(self, home: Home) -> LLMAdviceResult:
        """Produce a summary and a prioritized list of recommendations for a home.

        Raises:
            app.exceptions.LLMError: the provider call failed (network, auth, rate
                limit, server error).
            app.exceptions.LLMResponseParsingError: the provider responded but the
                content didn't match the expected shape.
        """
        raise NotImplementedError
