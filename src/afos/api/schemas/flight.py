from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FlightRead(BaseModel):
    """Public read model for Flight rows (operations dashboard / APIs)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    airline_code: str
    flight_number: str = Field(..., examples=["1234"])

    origin_iata: str
    destination_iata: str

    scheduled_departure_utc: datetime
    scheduled_arrival_utc: datetime
    actual_departure_utc: Optional[datetime] = None
    actual_arrival_utc: Optional[datetime] = None

    aircraft_tail: Optional[str] = None
    aircraft_type: Optional[str] = None
    status: str
