"""Domain-level exceptions.

These are raised by the service layer and translated to HTTP responses by the
exception handlers registered in app/main.py - keeps the service layer free of any
knowledge of HTTP status codes.
"""


class HomeNotFoundError(Exception):
    def __init__(self, home_id: str):
        self.home_id = home_id
        super().__init__(f"Home '{home_id}' was not found")


class LLMError(Exception):
    """Raised when the LLM provider fails (network, auth, rate limit, server error)."""


class LLMResponseParsingError(Exception):
    """Raised when the LLM's response cannot be parsed into the expected schema."""
