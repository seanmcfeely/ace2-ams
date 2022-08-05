from datetime import datetime
from sqlalchemy.orm import Session

from db import crud
from api_models.metadata_time import MetadataTimeCreate


def create_or_read(value: datetime, db: Session):
    return crud.metadata_time.create_or_read(model=MetadataTimeCreate(value=value), db=db)
