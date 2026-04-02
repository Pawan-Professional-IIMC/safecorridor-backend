import uuid
from sqlalchemy import Column, String, Integer, DateTime, JSON
from .database import Base
from datetime import datetime, timezone


class FlightStatusSnapshot(Base):
    __tablename__ = "flight_status_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    generated_at_utc = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    requested_airports = Column(JSON, default=list)
    per_airport_limit = Column(Integer, nullable=False, default=6)
    flight_status_filter = Column(String, nullable=True)
    total = Column(Integer, nullable=False, default=0)
    flights = Column(JSON, default=list)
