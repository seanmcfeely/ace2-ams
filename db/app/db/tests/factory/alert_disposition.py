from sqlalchemy.orm import Session
from typing import Optional

from db import crud
from api_models.alert_disposition import AlertDispositionCreate


def create_or_read(value: str, rank: int, db: Session, description: Optional[str] = None):
    return crud.alert_disposition.create_or_read(
        model=AlertDispositionCreate(description=description, value=value, rank=rank), db=db
    )
