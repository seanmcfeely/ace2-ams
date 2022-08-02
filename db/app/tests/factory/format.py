from sqlalchemy.orm import Session

import crud
from api_models.format import FormatCreate


def create_or_read(value: str, db: Session):
    return crud.format.create_or_read(model=FormatCreate(value=value), db=db)
