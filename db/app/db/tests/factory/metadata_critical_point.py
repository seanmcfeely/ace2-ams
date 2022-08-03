from sqlalchemy.orm import Session

from db import crud
from api_models.metadata_critical_point import MetadataCriticalPointCreate


def create_or_read(value: str, db: Session):
    return crud.metadata_critical_point.create_or_read(model=MetadataCriticalPointCreate(value=value), db=db)
