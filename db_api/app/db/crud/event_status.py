from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import UUID

from api_models.event_status import EventStatusCreate, EventStatusUpdate
from db import crud
from db.schemas.event_status import EventStatus


def create_or_read(model: EventStatusCreate, db: Session) -> EventStatus:
    obj = EventStatus(
        description=model.description,
        queues=crud.queue.read_by_values(values=model.queues, db=db),
        uuid=model.uuid,
        value=model.value,
    )

    if crud.helpers.create(obj=obj, db=db):
        return obj

    return read_by_value(value=model.value, db=db)


def delete(uuid: UUID, db: Session) -> bool:
    return crud.helpers.delete(uuid=uuid, db_table=EventStatus, db=db)


def read_all(db: Session) -> list[EventStatus]:
    return crud.helpers.read_all(db_table=EventStatus, order_by=EventStatus.value, db=db)


def read_by_uuid(uuid: UUID, db: Session) -> EventStatus:
    return crud.helpers.read_by_uuid(db_table=EventStatus, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> EventStatus:
    return crud.helpers.read_by_value(db_table=EventStatus, value=value, db=db)


def update(uuid: UUID, model: EventStatusUpdate, db: Session) -> bool:
    obj = read_by_uuid(uuid=uuid, db=db)

    # Get the data that was given in the request and use it to update the database object
    update_data = model.dict(exclude_unset=True)

    with db.begin_nested():
        try:
            if "description" in update_data:
                obj.description = update_data["description"]

            if "queues" in update_data:
                obj.queues = crud.queue.read_by_values(values=update_data["queues"], db=db)

            if "value" in update_data:
                obj.value = update_data["value"]

            db.flush()
            return True
        except IntegrityError:
            db.rollback()

    return False
