from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select
from uuid import UUID

from db import crud
from api_models.alert_disposition import AlertDispositionCreate, AlertDispositionUpdate
from db.schemas.alert_disposition import AlertDisposition


def build_read_all_query() -> Select:
    return select(AlertDisposition).order_by(AlertDisposition.rank)


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


def delete(uuid: UUID, db: Session) -> bool:
    return crud.helpers.delete(uuid=uuid, db_table=AlertDisposition, db=db)


def read_all(db: Session) -> list[AlertDisposition]:
    return db.execute(build_read_all_query()).scalars().all()


def read_by_uuid(uuid: UUID, db: Session) -> AlertDisposition:
    return crud.helpers.read_by_uuid(db_table=AlertDisposition, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> AlertDisposition:
    return crud.helpers.read_by_value(db_table=AlertDisposition, value=value, db=db)


def update(uuid: UUID, model: AlertDispositionUpdate, db: Session) -> bool:
    return crud.helpers.update(uuid=uuid, update_model=model, db_table=AlertDisposition, db=db)
