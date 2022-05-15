from sqlalchemy.orm import Session
from uuid import UUID

from api_models.event_prevention_tool import EventPreventionToolCreate
from db import crud
from db.schemas.event_prevention_tool import EventPreventionTool


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


def read_by_uuid(uuid: UUID, db: Session) -> EventPreventionTool:
    return crud.helpers.read_by_uuid(db_table=EventPreventionTool, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> EventPreventionTool:
    return crud.helpers.read_by_value(db_table=EventPreventionTool, value=value, db=db)


def read_by_values(values: list[str], db: Session) -> list[EventPreventionTool]:
    return crud.helpers.read_by_values(db_table=EventPreventionTool, values=values, db=db)
