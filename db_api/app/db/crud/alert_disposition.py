from sqlalchemy.orm import Session
from uuid import UUID

from api_models.alert_disposition import AlertDispositionCreate
from db import crud
from db.schemas.alert_disposition import AlertDisposition


def create_or_read(model: AlertDispositionCreate, db: Session) -> AlertDisposition:
    obj = AlertDisposition(**model.dict())

    if crud.helpers.create(obj=obj, db=db):
        return obj

    return read_by_value(value=model.value, db=db)


def read_all(db: Session) -> list[AlertDisposition]:
    return crud.helpers.read_all(db_table=AlertDisposition, db=db)


def read_by_uuid(uuid: UUID, db: Session) -> AlertDisposition:
    return crud.helpers.read_by_uuid(db_table=AlertDisposition, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> AlertDisposition:
    return crud.helpers.read_by_value(db_table=AlertDisposition, value=value, db=db)
