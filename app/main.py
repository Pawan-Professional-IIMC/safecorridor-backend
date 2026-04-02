import os
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import flights
from .database import SessionLocal
from .flight_snapshot_service import refresh_and_store_snapshot

logger = logging.getLogger(__name__)
FLIGHT_SNAPSHOT_REFRESH_ENABLED = os.getenv("FLIGHT_SNAPSHOT_REFRESH_ENABLED", "true").lower() == "true"
FLIGHT_SNAPSHOT_REFRESH_INTERVAL_SECONDS = int(os.getenv("FLIGHT_SNAPSHOT_REFRESH_INTERVAL_SECONDS", "43200"))

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SafeCorridor API",
    description="API for GCC flight status.",
    version="1.0.0"
)

raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["http://localhost:3000"],
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flights.router, prefix="/api/flights", tags=["Flights"])

@app.get("/api/health")
def read_root():
    return {"status": "ok", "service": "safecorridor-api"}


async def _flight_snapshot_refresh_loop() -> None:
    while True:
        db = SessionLocal()
        try:
            await refresh_and_store_snapshot(db)
        except Exception as exc:
            logger.exception("Flight snapshot refresh failed: %s", exc)
        finally:
            db.close()
        await asyncio.sleep(FLIGHT_SNAPSHOT_REFRESH_INTERVAL_SECONDS)


@app.on_event("startup")
async def start_background_tasks() -> None:
    if FLIGHT_SNAPSHOT_REFRESH_ENABLED:
        app.state.flight_snapshot_refresh_task = asyncio.create_task(_flight_snapshot_refresh_loop())


@app.on_event("shutdown")
async def stop_background_tasks() -> None:
    task = getattr(app.state, "flight_snapshot_refresh_task", None)
    if task is not None:
        task.cancel()
