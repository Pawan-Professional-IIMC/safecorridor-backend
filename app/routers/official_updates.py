from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter()


@router.get("/latest", response_model=schemas.OfficialUpdateSnapshotResponse)
def get_latest_official_update(db: Session = Depends(get_db)):
    snapshot = (
        db.query(models.OfficialUpdateSnapshot)
        .order_by(models.OfficialUpdateSnapshot.created_at.desc())
        .first()
    )
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No official updates snapshot available yet.",
        )
    return snapshot
