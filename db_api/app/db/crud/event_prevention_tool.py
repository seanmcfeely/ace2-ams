from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from api_models.event_prevention_tool import EventPreventionToolCreate
from db import crud
from db.schemas.event_prevention_tool import EventPreventionTool


def create(model: EventPreventionToolCreate, db: Session) -> EventPreventionTool:
    obj = read_by_value(value=model.value, db=db)

    if obj is None:
        obj = EventPreventionTool(**model.dict())
        db.add(obj)
        db.flush()

    return obj


def read_by_uuid(uuid: UUID, db: Session) -> EventPreventionTool:
    return crud.helpers.read_by_uuid(db_table=EventPreventionTool, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> Optional[EventPreventionTool]:
    return crud.helpers.read_by_value(db_table=EventPreventionTool, value=value, db=db)
