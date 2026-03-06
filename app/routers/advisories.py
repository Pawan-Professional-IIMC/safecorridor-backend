from fastapi import APIRouter, Depends, Query
from sqlalchemy import cast, String
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter()


def _json_array_contains(column, value: str):
    # JSON is stored as an array of strings; cast to text so the filter works on PostgreSQL and SQLite.
    return cast(column, String).like(f'%"{value}"%')

@router.get("/", response_model=List[schemas.AdvisoryResponse])
@router.get("", response_model=List[schemas.AdvisoryResponse], include_in_schema=False)
def get_advisories(
    airport_icao: Optional[str] = None,
    fir_code: Optional[str] = None,
    airline: Optional[str] = None,
    source_type: Optional[models.AdvisorySourceType] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(models.Advisory)
    query = query.filter(models.Advisory.source_name != "SafeCorridor Seed Data")
    
    if airport_icao:
        query = query.filter(_json_array_contains(models.Advisory.airports_icao, airport_icao))
    if fir_code:
        query = query.filter(_json_array_contains(models.Advisory.fir_codes, fir_code))
    if airline:
        query = query.filter(_json_array_contains(models.Advisory.airlines, airline))
    if source_type:
        query = query.filter(models.Advisory.source_type == source_type)
        
    query = query.order_by(models.Advisory.created_at.desc())
    offset = (page - 1) * size
    return query.offset(offset).limit(size).all()
