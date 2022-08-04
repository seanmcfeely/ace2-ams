from sqlalchemy.orm import Session

from db import crud
from api_models.metadata_display_type import MetadataDisplayTypeCreate


def create_or_read(value: str, db: Session):
    return crud.metadata_display_type.create_or_read(model=MetadataDisplayTypeCreate(value=value), db=db)
