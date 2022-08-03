from sqlalchemy.orm import Session

from db import crud
from api_models.metadata_detection_point import MetadataDetectionPointCreate


def create_or_read(value: str, db: Session):
    return crud.metadata_detection_point.create_or_read(model=MetadataDetectionPointCreate(value=value), db=db)
