from sqlalchemy.orm import Session

from db import crud
from api_models.observable_type import ObservableTypeCreate


def create_or_read(value: str, db: Session):
    return crud.observable_type.create_or_read(model=ObservableTypeCreate(value=value), db=db)
