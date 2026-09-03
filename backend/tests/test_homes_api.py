from fastapi.testclient import TestClient

from tests.conftest import VALID_HOME_PAYLOAD


def test_create_home_returns_201_with_generated_id(client: TestClient) -> None:
    response = client.post("/api/homes", json=VALID_HOME_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["size_sqm"] == VALID_HOME_PAYLOAD["size_sqm"]
    assert body["heating_type"] == "gas"
    assert body["insulation_quality"] == "poor"
    assert body["occupants"] == 3
    assert "created_at" in body


def test_create_home_occupants_is_optional(client: TestClient) -> None:
    payload = {**VALID_HOME_PAYLOAD}
    del payload["occupants"]

    response = client.post("/api/homes", json=payload)

    assert response.status_code == 201
    assert response.json()["occupants"] is None


def test_create_home_rejects_invalid_heating_type(client: TestClient) -> None:
    payload = {**VALID_HOME_PAYLOAD, "heating_type": "coal"}

    response = client.post("/api/homes", json=payload)

    assert response.status_code == 422


def test_create_home_rejects_negative_size(client: TestClient) -> None:
    payload = {**VALID_HOME_PAYLOAD, "size_sqm": -10}

    response = client.post("/api/homes", json=payload)

    assert response.status_code == 422


def test_create_home_rejects_future_year_built(client: TestClient) -> None:
    payload = {**VALID_HOME_PAYLOAD, "year_built": 3000}

    response = client.post("/api/homes", json=payload)

    assert response.status_code == 422


def test_get_home_returns_previously_created_home(client: TestClient) -> None:
    created = client.post("/api/homes", json=VALID_HOME_PAYLOAD).json()

    response = client.get(f"/api/homes/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_home_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.get("/api/homes/does-not-exist")

    assert response.status_code == 404
    assert "does-not-exist" in response.json()["detail"]
