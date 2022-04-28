from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from typing import Any, Optional
from uuid import UUID


def read_by_uuid(db_table: DeclarativeMeta, uuid: UUID, db: Session) -> Any:
    """Returns the object with the specific UUID from the given database table."""

    return db.execute(select(db_table).where(db_table.uuid == uuid)).scalars().one()


def read_by_uuids(uuids: list[UUID], db_table: DeclarativeMeta, db: Session) -> list[Any]:
    """Returns a list of objects with the given UUIDs. Raises an exception if the number of objects
    returned from the database does not match the number of unique given UUIDs."""

    if not uuids:
        return uuids

    unique_uuids = list(set(uuids))
    result = db.execute(select(db_table).where(db_table.uuid.in_(unique_uuids))).scalars().all()

    if len(unique_uuids) != len(result):
        raise ValueError("One or more UUIDs was not found in the database.")

    return result


def read_by_value(db_table: DeclarativeMeta, value: str, db: Session) -> Optional[Any]:
    """Returns the object with the specific value (if it exists) from the given database table."""

    return db.execute(select(db_table).where(db_table.value == value)).scalars().one_or_none()


def read_by_values(db_table: DeclarativeMeta, values: list[str], db: Session) -> list[Any]:
    """Returns a list of objects with the specific values from the given database table. Raise an
    exception if the number of objects returned from the database does not match the number of
    unique given values."""

    if not values:
        return []

    unique_values = set(values)
    result = db.execute(select(db_table).where(db_table.value.in_(values))).scalars().all()

    if len(unique_values) != len(result):
        raise ValueError("One or more values was not found in the database.")

    return result


def utcnow() -> datetime:
    """Returns a timezone-aware version of datetime.utcnow()."""

    return datetime.now(timezone.utc)
