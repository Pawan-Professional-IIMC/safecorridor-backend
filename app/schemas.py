from pydantic import BaseModel, UUID4, Field
from typing import List, Optional, Any
from datetime import datetime


class FlightStatusEntry(BaseModel):
    provider: str
    status: str
    status_label: str
    flight_date: Optional[str] = None
    departure_airport_code: str
    departure_airport: Optional[str] = None
    departure_iata: Optional[str] = None
    departure_icao: Optional[str] = None
    departure_terminal: Optional[str] = None
    departure_gate: Optional[str] = None
    departure_delay_minutes: Optional[int] = None
    departure_scheduled_utc: Optional[datetime | str] = None
    departure_estimated_utc: Optional[datetime | str] = None
    departure_actual_utc: Optional[datetime | str] = None
    arrival_airport: Optional[str] = None
    arrival_iata: Optional[str] = None
    arrival_icao: Optional[str] = None
    arrival_timezone: Optional[str] = None
    destination_country: Optional[str] = None
    arrival_terminal: Optional[str] = None
    arrival_gate: Optional[str] = None
    arrival_baggage: Optional[str] = None
    arrival_delay_minutes: Optional[int] = None
    arrival_scheduled_utc: Optional[datetime | str] = None
    arrival_estimated_utc: Optional[datetime | str] = None
    airline_name: Optional[str] = None
    airline_iata: Optional[str] = None
    airline_icao: Optional[str] = None
    flight_number: Optional[str] = None
    flight_iata: Optional[str] = None
    flight_icao: Optional[str] = None
    flight_codeshared: Optional[Any] = None
    aircraft_registration: Optional[str] = None
    aircraft_icao24: Optional[str] = None
    live_latitude: Optional[float] = None
    live_longitude: Optional[float] = None
    live_altitude: Optional[float] = None
    live_speed_horizontal: Optional[float] = None
    live_is_ground: Optional[bool] = None


class FlightStatusSnapshotResponse(BaseModel):
    source_name: str
    source_type: str
    generated_at_utc: datetime
    requested_airports: List[str] = Field(default_factory=list)
    total: int
    flights: List[FlightStatusEntry] = Field(default_factory=list)
