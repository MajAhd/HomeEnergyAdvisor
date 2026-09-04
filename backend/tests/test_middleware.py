import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_llm_client
from app.api.middleware import log_requests
from app.exceptions import LLMError
from app.main import app
from tests.conftest import VALID_HOME_PAYLOAD
from tests.test_advice_api import RaisingLLMClient


def test_response_includes_a_generated_request_id_header(client: TestClient) -> None:
    # Act
    response = client.get("/health")

    # Assert
    assert response.headers["X-Request-ID"]


def test_response_echoes_a_client_supplied_request_id(client: TestClient) -> None:
    # Act
    response = client.get("/health", headers={"X-Request-ID": "test-request-id"})

    # Assert
    assert response.headers["X-Request-ID"] == "test-request-id"


def test_successful_request_is_logged_at_info(client: TestClient, caplog) -> None:
    # Act
    with caplog.at_level(logging.INFO):
        client.get("/health")

    # Assert
    info_lines = [r for r in caplog.records if r.name == "app.http" and r.levelname == "INFO"]
    assert any("GET /health -> 200" in r.getMessage() for r in info_lines)


def test_not_found_request_is_logged_at_warning(client: TestClient, caplog) -> None:
    # Act
    with caplog.at_level(logging.INFO):
        client.get("/api/homes/does-not-exist")

    # Assert
    warning_lines = [r for r in caplog.records if r.name == "app.http" and r.levelname == "WARNING"]
    assert any("-> 404" in r.getMessage() for r in warning_lines)


def test_llm_failure_is_logged_at_error(client: TestClient, caplog) -> None:
    # Arrange
    home_id = client.post("/api/homes", json=VALID_HOME_PAYLOAD).json()["id"]
    app.dependency_overrides[get_llm_client] = lambda: RaisingLLMClient(
        LLMError("provider unreachable")
    )

    # Act
    with caplog.at_level(logging.INFO):
        client.post(f"/api/homes/{home_id}/advice")

    # Assert
    error_lines = [r for r in caplog.records if r.levelname == "ERROR"]
    # Both the exception handler (with the underlying reason) and the request-log
    # middleware (with the status code) log this failure at ERROR.
    assert any("provider unreachable" in r.getMessage() for r in error_lines)
    assert any("-> 502" in r.getMessage() for r in error_lines)


def test_unhandled_exception_is_logged_and_reraised(caplog) -> None:
    """log_requests is exercised directly against a throwaway app here (rather than
    the real `app`) so we can trigger a truly unhandled exception - one with no
    registered @app.exception_handler - without weakening the real app's own
    exception handling."""
    # Arrange
    probe_app = FastAPI()
    probe_app.middleware("http")(log_requests)

    @probe_app.get("/boom")
    def boom() -> None:
        raise ValueError("kaboom")

    probe_client = TestClient(probe_app, raise_server_exceptions=False)

    # Act
    with caplog.at_level(logging.INFO):
        response = probe_client.get("/boom")

    # Assert
    assert response.status_code == 500
    error_lines = [r for r in caplog.records if r.name == "app.http" and r.levelname == "ERROR"]
    assert any("unhandled exception" in r.getMessage() for r in error_lines)
