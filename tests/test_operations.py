from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from afos.api.app import create_app
from afos.db.models.flight import Flight


def test_database_health_endpoint(sqlite_memory_session) -> None:
    with TestClient(create_app()) as client:
        r = client.get("/v1/ops/db-health")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    assert payload["scalar"] == 1


def test_readiness_endpoint(sqlite_memory_session) -> None:
    with TestClient(create_app()) as client:
        r = client.get("/v1/ops/ready")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ready"
    assert payload["database"] == "ok"
    assert "llm_configured" in payload


def test_list_flights_filtered(sqlite_memory_session) -> None:
    SessionLocal = sqlite_memory_session
    departure = datetime(2026, 5, 10, 18, 15, tzinfo=timezone.utc)
    arrival = departure + timedelta(hours=4, minutes=33)

    with SessionLocal.begin() as db:
        flight = Flight(
            airline_code="UA",
            flight_number="1842",
            origin_iata="ORD",
            destination_iata="DEN",
            scheduled_departure_utc=departure,
            scheduled_arrival_utc=arrival,
            aircraft_tail="N37513",
            aircraft_type="739",
            actual_departure_utc=departure + timedelta(minutes=72),
            status="delayed",
        )
        db.add(flight)

    with TestClient(create_app()) as client:
        r = client.get("/v1/ops/flights", params={"limit": 5, "airline_code": "ua"})

    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["flight_number"] == "1842"
    assert rows[0]["status"] == "delayed"
    assert rows[0]["origin_iata"] == "ORD"
    assert rows[0]["destination_iata"] == "DEN"
    assert rows[0]["aircraft_tail"] == "N37513"
