from sqlalchemy.orm import Session

import crud
from api_models.metadata_sort import MetadataSortCreate


def create_or_read(value: int, db: Session):
    return crud.metadata_sort.create_or_read(model=MetadataSortCreate(value=value), db=db)
