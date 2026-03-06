import os
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Iterable

import httpx
from dotenv import load_dotenv


load_dotenv()

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
AVIATIONSTACK_BASE_URL = os.getenv("AVIATIONSTACK_BASE_URL", "https://api.aviationstack.com/v1")
AVIATIONSTACK_CACHE_TTL_SECONDS = int(os.getenv("AVIATIONSTACK_CACHE_TTL_SECONDS", "300"))

DEFAULT_UAE_DEPARTURE_AIRPORTS = ("DXB", "DWC", "AUH", "SHJ")

_flight_cache: dict[tuple[str, int, str | None], dict] = {}
_flight_cache_lock = asyncio.Lock()


class AviationstackError(RuntimeError):
    pass


def _to_iso8601(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except ValueError:
        return value


def _normalize_flight_status(value: str | None) -> str:
    normalized = (value or "unknown").strip().lower().replace(" ", "_")
    allowed = {
        "scheduled",
        "active",
        "landed",
        "cancelled",
        "incident",
        "diverted",
        "unknown",
    }
    if normalized in allowed:
        return normalized
    if normalized in {"delayed"}:
        return normalized
    return "unknown"


def normalize_aviationstack_flight(item: dict, departure_airport_code: str) -> dict:
    departure = item.get("departure") or {}
    arrival = item.get("arrival") or {}
    airline = item.get("airline") or {}
    flight = item.get("flight") or {}
    live = item.get("live") or {}

    return {
        "provider": "aviationstack",
        "status": _normalize_flight_status(item.get("flight_status")),
        "status_label": item.get("flight_status") or "unknown",
        "flight_date": item.get("flight_date"),
        "departure_airport_code": departure_airport_code,
        "departure_airport": departure.get("airport"),
        "departure_iata": departure.get("iata"),
        "departure_icao": departure.get("icao"),
        "departure_terminal": departure.get("terminal"),
        "departure_gate": departure.get("gate"),
        "departure_delay_minutes": departure.get("delay"),
        "departure_scheduled_utc": _to_iso8601(departure.get("scheduled")),
        "departure_estimated_utc": _to_iso8601(departure.get("estimated")),
        "departure_actual_utc": _to_iso8601(departure.get("actual")),
        "arrival_airport": arrival.get("airport"),
        "arrival_iata": arrival.get("iata"),
        "arrival_icao": arrival.get("icao"),
        "arrival_terminal": arrival.get("terminal"),
        "arrival_gate": arrival.get("gate"),
        "arrival_baggage": arrival.get("baggage"),
        "arrival_delay_minutes": arrival.get("delay"),
        "arrival_scheduled_utc": _to_iso8601(arrival.get("scheduled")),
        "arrival_estimated_utc": _to_iso8601(arrival.get("estimated")),
        "airline_name": airline.get("name"),
        "airline_iata": airline.get("iata"),
        "airline_icao": airline.get("icao"),
        "flight_number": flight.get("number"),
        "flight_iata": flight.get("iata"),
        "flight_icao": flight.get("icao"),
        "flight_codeshared": item.get("codeshared"),
        "aircraft_registration": live.get("registration"),
        "aircraft_icao24": live.get("icao24"),
        "live_latitude": live.get("latitude"),
        "live_longitude": live.get("longitude"),
        "live_altitude": live.get("altitude"),
        "live_speed_horizontal": live.get("speed_horizontal"),
        "live_is_ground": live.get("is_ground"),
    }


async def fetch_departures_for_airport(
    departure_airport_code: str,
    *,
    limit: int = 10,
    flight_status: str | None = None,
) -> list[dict]:
    if not AVIATIONSTACK_API_KEY:
        raise AviationstackError("AVIATIONSTACK_API_KEY is not configured.")

    cache_key = (departure_airport_code, limit, flight_status)
    now = datetime.now(timezone.utc)

    async with _flight_cache_lock:
        cached = _flight_cache.get(cache_key)
        if cached and cached["expires_at"] > now:
            return cached["data"]

    params = {
        "access_key": AVIATIONSTACK_API_KEY,
        "dep_iata": departure_airport_code,
        "limit": limit,
    }
    if flight_status:
        params["flight_status"] = flight_status

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{AVIATIONSTACK_BASE_URL}/flights", params=params)
        response.raise_for_status()
        payload = response.json()

    error = payload.get("error")
    if error:
        message = error.get("message") or error.get("type") or "Aviationstack request failed."
        raise AviationstackError(message)

    normalized_flights = [
        normalize_aviationstack_flight(item, departure_airport_code)
        for item in payload.get("data", [])
    ]

    fetched_at = datetime.now(timezone.utc)
    async with _flight_cache_lock:
        _flight_cache[cache_key] = {
            "data": normalized_flights,
            "expires_at": fetched_at + timedelta(seconds=AVIATIONSTACK_CACHE_TTL_SECONDS),
        }

    return normalized_flights


async def fetch_uae_departures(
    departure_airport_codes: Iterable[str] | None = None,
    *,
    per_airport_limit: int = 10,
    flight_status: str | None = None,
) -> list[dict]:
    flights: list[dict] = []
    for airport_code in departure_airport_codes or DEFAULT_UAE_DEPARTURE_AIRPORTS:
        flights.extend(
            await fetch_departures_for_airport(
                airport_code.strip().upper(),
                limit=per_airport_limit,
                flight_status=flight_status,
            )
        )
    return flights
