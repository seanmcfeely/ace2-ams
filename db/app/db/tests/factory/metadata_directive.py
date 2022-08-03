from sqlalchemy.orm import Session

from db import crud
from api_models.metadata_directive import MetadataDirectiveCreate


def create_or_read(value: str, db: Session):
    return crud.metadata_directive.create_or_read(model=MetadataDirectiveCreate(value=value), db=db)
