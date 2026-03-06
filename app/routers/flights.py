from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..integrations.aviationstack import (
    AviationstackError,
    DEFAULT_UAE_DEPARTURE_AIRPORTS,
    fetch_uae_departures,
)
from ..schemas import FlightStatusSnapshotResponse


router = APIRouter()


@router.get("/status", response_model=FlightStatusSnapshotResponse)
async def get_flight_status(
    airports: Optional[str] = Query(
        default=",".join(DEFAULT_UAE_DEPARTURE_AIRPORTS),
        description="Comma-separated UAE departure airport IATA codes, e.g. DXB,AUH,SHJ",
    ),
    per_airport_limit: int = Query(default=8, ge=1, le=25),
    flight_status: Optional[str] = Query(default=None),
):
    airport_codes = [code.strip().upper() for code in (airports or "").split(",") if code.strip()]
    if not airport_codes:
        airport_codes = list(DEFAULT_UAE_DEPARTURE_AIRPORTS)

    try:
        flights = await fetch_uae_departures(
            airport_codes,
            per_airport_limit=per_airport_limit,
            flight_status=flight_status,
        )
    except AviationstackError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Failed to fetch flight status feed.") from exc

    flights.sort(
        key=lambda item: (
            item.get("departure_estimated_utc")
            or item.get("departure_scheduled_utc")
            or "",
            item.get("flight_iata") or "",
        )
    )

    return FlightStatusSnapshotResponse(
        source_name="Aviationstack",
        source_type="flight_status_api",
        generated_at_utc=datetime.now(timezone.utc),
        requested_airports=airport_codes,
        total=len(flights),
        flights=flights,
    )
