from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from api_models.event_remediation import EventRemediationCreate
from db import crud
from db.schemas.event_remediation import EventRemediation


def create(model: EventRemediationCreate, db: Session) -> EventRemediation:
    obj = read_by_value(value=model.value, db=db)

    if obj is None:
        obj = EventRemediation(**model.dict())
        db.add(obj)
        db.flush()

    return obj


def read_by_uuid(uuid: UUID, db: Session) -> EventRemediation:
    return crud.helpers.read_by_uuid(db_table=EventRemediation, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> Optional[EventRemediation]:
    return crud.helpers.read_by_value(db_table=EventRemediation, value=value, db=db)
