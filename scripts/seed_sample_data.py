#!/usr/bin/env python
"""
Populate the database with realistic airline-operations demo data.

Run after migrations:

  cd agentic-flight-ops-intel
  source .venv/bin/activate
  export PYTHONPATH=src
  mkdir -p data
  DATABASE_URL=sqlite:///./data/afois_local.db alembic upgrade head
  DATABASE_URL=sqlite:///./data/afois_local.db python scripts/seed_sample_data.py
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import func, select

from afos.db.models.delay_event import DelayEvent
from afos.db.models.flight import Flight
from afos.db.models.policy_document import PolicyDocument
from afos.db.session import get_session_factory


def utc(*parts: int) -> datetime:
    return datetime(*parts, tzinfo=timezone.utc)


def main() -> None:
    sf = get_session_factory()

    policies = [
        PolicyDocument(
            doc_code="IRREG-GEN-2024",
            title="Irregular Operations — Passenger Re-accommodation Principles",
            section_ref="4.2",
            category="irregular_operations",
            effective_from=date(2024, 1, 1),
            body_text=(
                "During controllable disruptions, re-book passengers on the "
                "next available option with comparable cabin class when inventory "
                "permits; document reason codes consistently for auditing. "
                "Meal and hotel vouchers follow station procedure when delay exceeds "
                "published thresholds applicable to hub versus outstation staffing."
            ),
        ),
        PolicyDocument(
            doc_code="SCHED-MINCONN-OPS",
            title="Operational Minimum Connection Guidance (International)",
            section_ref="MCT-Appendix-A",
            category="connections",
            effective_from=date(2023, 6, 1),
            body_text=(
                "Default international-to-international minimum connection times "
                "differ by inbound terminal and remote stand usage; coordinators "
                "should consult published minima before confirming tight itineraries "
                "flagged by operations control watch lists."
            ),
        ),
    ]

    baseline = utc(2026, 5, 11, 10, 0)
    demo_flights = [
        Flight(
            airline_code="UA",
            flight_number="1842",
            origin_iata="ORD",
            destination_iata="DEN",
            scheduled_departure_utc=baseline.replace(hour=18, minute=45),
            scheduled_arrival_utc=baseline.replace(hour=21, minute=42),
            aircraft_tail="N37513",
            aircraft_type="737-900",
            actual_departure_utc=baseline.replace(hour=19, minute=52),
            status="delayed",
        ),
        Flight(
            airline_code="UA",
            flight_number="0955",
            origin_iata="SFO",
            destination_iata="EWR",
            scheduled_departure_utc=baseline.replace(hour=13, minute=55),
            scheduled_arrival_utc=baseline.replace(hour=22, minute=37),
            aircraft_tail="N14016",
            aircraft_type="757-300",
            status="scheduled",
        ),
        Flight(
            airline_code="UA",
            flight_number="1204",
            origin_iata="IAH",
            destination_iata="MEX",
            scheduled_departure_utc=baseline.replace(hour=16, minute=35),
            scheduled_arrival_utc=baseline.replace(hour=19, minute=5),
            aircraft_tail="N69824",
            aircraft_type="737-800",
            actual_departure_utc=None,
            status="scheduled",
        ),
    ]

    with sf.begin() as db:
        flights_count = db.scalar(select(func.count()).select_from(Flight)) or 0
        if flights_count > 0:
            print("Seed skipped — flights already populated.")
            return

        existing_codes = set(db.scalars(select(PolicyDocument.doc_code)).all())
        for p in policies:
            if p.doc_code not in existing_codes:
                db.add(p)

        for f in demo_flights:
            db.add(f)

        db.flush()

        ua1842 = db.scalars(
            select(Flight).where(
                Flight.flight_number == "1842",
                Flight.scheduled_departure_utc == baseline.replace(hour=18, minute=45),
            )
        ).first()
        if ua1842 is None:
            raise RuntimeError("Expected demo flight 1842 after flush.")

        db.add(
            DelayEvent(
                flight_id=ua1842.id,
                delay_minutes=67,
                reason_category="crew",
                reason_detail="Duty-time extension threshold required swap to reserve crew bucket.",
                recorded_by_system="seed_script",
                recorded_at_utc=utc(2026, 5, 11, 19, 0),
            )
        )


if __name__ == "__main__":
    main()
    print("Seed complete.")
