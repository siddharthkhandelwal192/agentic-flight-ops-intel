from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from afos.db.base import Base

if TYPE_CHECKING:
    from afos.db.models.delay_event import DelayEvent


class Flight(Base):
    """Scheduled / actual flight instance for operations intelligence."""

    __tablename__ = "flights"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    airline_code: Mapped[str] = mapped_column(String(3), nullable=False, default="UA", index=True)
    flight_number: Mapped[str] = mapped_column(String(16), nullable=False)

    origin_iata: Mapped[str] = mapped_column(String(3), nullable=False)
    destination_iata: Mapped[str] = mapped_column(String(3), nullable=False)

    scheduled_departure_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_arrival_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    actual_departure_utc: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_arrival_utc: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    aircraft_tail: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    aircraft_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    status: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="scheduled",
        server_default="scheduled",
        comment="scheduled, boarded, departed, arrived, diverted, cancelled, delayed",
    )

    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    delay_events: Mapped[List["DelayEvent"]] = relationship(
        back_populates="flight",
        cascade="all, delete-orphan",
    )
