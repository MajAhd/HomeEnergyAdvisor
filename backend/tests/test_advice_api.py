from fastapi.testclient import TestClient

from app.api.deps import get_llm_client
from app.db.models import Home
from app.exceptions import LLMError, LLMResponseParsingError
from app.llm.base import LLMClient
from app.main import app
from tests.conftest import VALID_HOME_PAYLOAD


class RaisingLLMClient(LLMClient):
    """Test double that always fails, to exercise the error-handling paths."""

    def __init__(self, exc: Exception):
        self._exc = exc

    def generate_advice(self, home: Home):
        raise self._exc


def test_advice_returns_prioritized_recommendations(client: TestClient) -> None:
    # Arrange
    home_id = client.post("/api/homes", json=VALID_HOME_PAYLOAD).json()["id"]

    # Act
    response = client.post(f"/api/homes/{home_id}/advice")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["home_id"] == home_id
    assert body["source"] == "mock"
    assert body["summary"]
    assert len(body["recommendations"]) >= 3
    for rec in body["recommendations"]:
        assert rec["priority"] in ("high", "medium", "low")
        assert rec["title"]
        assert rec["description"]
        assert rec["category"]

    # A poorly-insulated, gas-heated home should surface at least one high-priority item.
    assert any(rec["priority"] == "high" for rec in body["recommendations"])


def test_advice_returns_404_for_unknown_home(client: TestClient) -> None:
    # Act
    response = client.post("/api/homes/does-not-exist/advice")

    # Assert
    assert response.status_code == 404


def test_advice_returns_502_when_llm_provider_fails(client: TestClient) -> None:
    # Arrange
    home_id = client.post("/api/homes", json=VALID_HOME_PAYLOAD).json()["id"]
    app.dependency_overrides[get_llm_client] = lambda: RaisingLLMClient(
        LLMError("provider unreachable")
    )

    # Act
    response = client.post(f"/api/homes/{home_id}/advice")

    # Assert
    assert response.status_code == 502
    assert "provider unreachable" in response.json()["detail"]


def test_advice_returns_502_when_llm_response_is_unparseable(client: TestClient) -> None:
    # Arrange
    home_id = client.post("/api/homes", json=VALID_HOME_PAYLOAD).json()["id"]
    app.dependency_overrides[get_llm_client] = lambda: RaisingLLMClient(
        LLMResponseParsingError("bad shape")
    )

    # Act
    response = client.post(f"/api/homes/{home_id}/advice")

    # Assert
    assert response.status_code == 502
