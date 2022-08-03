from sqlalchemy.orm import Session

from db import crud
from api_models.queue import QueueCreate


def create_or_read(value: str, db: Session):
    return crud.queue.create_or_read(model=QueueCreate(value=value), db=db)
