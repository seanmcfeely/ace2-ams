from sqlalchemy.orm import Session

from db import crud
from api_models.metadata_display_value import MetadataDisplayValueCreate


def create_or_read(value: str, db: Session):
    return crud.metadata_display_value.create_or_read(model=MetadataDisplayValueCreate(value=value), db=db)
