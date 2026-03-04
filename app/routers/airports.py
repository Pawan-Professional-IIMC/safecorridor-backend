from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/status", response_model=List[schemas.AirportResponse])
def get_airports_status(
    country: Optional[str] = None,
    status: Optional[models.StatusEnum] = None,
    airspace_status: Optional[models.AirspaceStatusEnum] = None,
    airline_operations: Optional[models.AirlineOperationsEnum] = None,
    is_hub: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Airport)
    if country:
        query = query.filter(models.Airport.country == country)
    if status is not None:
        query = query.filter(models.Airport.status == status)
    if airspace_status is not None:
        query = query.filter(models.Airport.airspace_status == airspace_status.value)
    if airline_operations is not None:
        query = query.filter(models.Airport.airline_operations == airline_operations.value)
    if is_hub is not None:
        query = query.filter(models.Airport.is_hub == is_hub)
    return query.all()
