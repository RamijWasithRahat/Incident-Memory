from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(app)


def test_invalid_incident_payload_returns_422(
) -> None:
    response = client.post(
        "/api/incidents",
        json={
            "incident_code": "",
            "title": "",
        },
    )

    assert (
        response.status_code
        == 422
    )


def test_health_endpoint_still_works(
) -> None:
    response = client.get(
        "/health"
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["api"]
        == "up"
    )