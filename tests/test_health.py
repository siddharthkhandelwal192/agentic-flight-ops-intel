from fastapi.testclient import TestClient

from afos.api.app import create_app


def test_health_ok() -> None:
    with TestClient(create_app()) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["service"] == "afois-api"
        assert "X-Request-Id" in r.headers

