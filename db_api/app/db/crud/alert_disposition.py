from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from uuid import UUID

from api_models.alert_disposition import AlertDispositionCreate
from db import crud
from db.schemas.alert_disposition import AlertDisposition


def create_or_read(model: AlertDispositionCreate, db: Session) -> AlertDisposition:
    obj = AlertDisposition(**model.dict())

    if crud.helpers.create(obj=obj, db=db):
        return obj

    return (
        db.execute(
            select(AlertDisposition).where(
                or_(
                    AlertDisposition.rank == model.rank,
                    AlertDisposition.uuid == model.uuid,
                    AlertDisposition.value == model.value,
                )
            )
        )
        .scalars()
        .one()
    )


def read_by_uuid(uuid: UUID, db: Session) -> AlertDisposition:
    return crud.helpers.read_by_uuid(db_table=AlertDisposition, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> AlertDisposition:
    return crud.helpers.read_by_value(db_table=AlertDisposition, value=value, db=db)
