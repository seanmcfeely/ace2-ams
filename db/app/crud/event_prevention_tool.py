from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select
from uuid import UUID

import crud
from api_models.event_prevention_tool import EventPreventionToolCreate, EventPreventionToolUpdate
from schemas.event_prevention_tool import EventPreventionTool


def build_read_all_query() -> Select:
    return select(EventPreventionTool).order_by(EventPreventionTool.value)


def create_or_read(model: EventPreventionToolCreate, db: Session) -> EventPreventionTool:
    obj = EventPreventionTool(
        description=model.description,
        queues=crud.queue.read_by_values(values=model.queues, db=db),
        uuid=model.uuid,
        value=model.value,
    )

    if crud.helpers.create(obj=obj, db=db):
        return obj

    return read_by_value(value=model.value, db=db)


def delete(uuid: UUID, db: Session) -> bool:
    return crud.helpers.delete(uuid=uuid, db_table=EventPreventionTool, db=db)


def read_all(db: Session) -> list[EventPreventionTool]:
    return db.execute(build_read_all_query()).scalars().all()


def read_by_uuid(uuid: UUID, db: Session) -> EventPreventionTool:
    return crud.helpers.read_by_uuid(db_table=EventPreventionTool, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> EventPreventionTool:
    return crud.helpers.read_by_value(db_table=EventPreventionTool, value=value, db=db)


def read_by_values(values: list[str], db: Session) -> list[EventPreventionTool]:
    return crud.helpers.read_by_values(db_table=EventPreventionTool, values=values, db=db)


def update(uuid: UUID, model: EventPreventionToolUpdate, db: Session) -> bool:
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
