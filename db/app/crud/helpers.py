import contextlib

from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy import select, update as sql_update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session, undefer
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.sql.selectable import Select
from typing import Any, Union
from urllib.parse import urlparse
from uuid import UUID

from api_models.summaries import URLDomainSummary, URLDomainSummaryIndividual
from exceptions import UuidNotFoundInDatabase, ValueNotFoundInDatabase
from schemas.observable import Observable


def create(obj: Any, db: Session) -> bool:
    """Uses a nested transaction to attempt to add the given object to the database. If it fails due
    to an IntegrityError, only the nested transaction is rolled back."""

    with db.begin_nested():
        with contextlib.suppress(IntegrityError):
            db.add(obj)
            db.flush()
            return True

    return False


def delete(uuid: UUID, db_table: DeclarativeMeta, db: Session) -> bool:
    """Uses a nested transaction to attempt to delete the given object from the database. If it fails due
    to an IntegrityError, only the nested transaction is rolled back."""

    # Ensure the record exists in the database
    obj = read_by_uuid(uuid=uuid, db_table=db_table, db=db)

    with db.begin_nested():
        try:
            db.delete(obj)
            db.flush()
            return True
        except IntegrityError:
            db.rollback()

    return False


def exists(uuid: UUID, db_table: DeclarativeMeta, db: Session):
    """Returns True/False if the UUID exists in the given table."""

    if not db.execute(select(db_table.uuid).where(db_table.uuid == uuid)).scalar():
        raise UuidNotFoundInDatabase(f"UUID {uuid} was not found in the {db_table.__tablename__} table.")


def read_by_uuid(db_table: DeclarativeMeta, uuid: UUID, db: Session, undefer_column: str = None) -> Any:
    """Returns the object with the specific UUID from the given database table."""

    query: Select = select(db_table).where(db_table.uuid == uuid)
    if undefer_column is not None:
        query = query.options(undefer(undefer_column))

    try:
        return db.execute(query).scalars().one()
    except NoResultFound as e:
        raise UuidNotFoundInDatabase(f"UUID {uuid} was not found in the {db_table.__tablename__} table.") from e


def read_by_value(db_table: DeclarativeMeta, value: Union[int, str], db: Session) -> Any:
    """Returns the object with the specific value (if it exists) from the given database table."""

    try:
        return db.execute(select(db_table).where(db_table.value == value)).scalars().one()
    except NoResultFound as e:
        raise ValueNotFoundInDatabase(
            f"The '{value}' value was not found in the {db_table.__tablename__} table."
        ) from e


def read_by_values(
    db_table: DeclarativeMeta, values: Union[list[int], list[str]], db: Session, error_on_not_found: bool = True
) -> list[Any]:
    """Returns a list of objects with the specific values from the given database table. Raise an
    exception if the number of objects returned from the database does not match the number of
    unique given values."""

    if not values:
        return []

    unique_values = set(values)
    result = db.execute(select(db_table).where(db_table.value.in_(values))).scalars().all()

    if error_on_not_found and len(unique_values) != len(result):
        for value in unique_values:
            if all(r.value != value for r in result):
                raise ValueNotFoundInDatabase(
                    f"The '{value}' value was not found in the {db_table.__tablename__} table."
                )

    return result


def update(uuid: UUID, update_model: BaseModel, db_table: DeclarativeMeta, db: Session) -> bool:
    """Uses a nested transaction to attempt to update the given object in the database. If it fails due
    to an IntegrityError, only the nested transaction is rolled back."""

    # Ensure the record exists in the database
    read_by_uuid(uuid=uuid, db_table=db_table, db=db)

    with db.begin_nested():
        try:
            result = db.execute(
                sql_update(db_table)
                .where(db_table.uuid == uuid)
                .values(
                    # exclude_unset is needed so that any values in the Pydantic model that are not
                    # being updated are not set to None. Instead they will be removed from the dict.
                    **update_model.dict(exclude_unset=True)
                )
            )
            return result.rowcount == 1
        except IntegrityError:
            db.rollback()

    return False


def utcnow() -> datetime:
    """Returns a timezone-aware version of datetime.utcnow()."""

    return datetime.now(timezone.utc)


def read_summary_url_domain(url_observables: list[Observable]) -> URLDomainSummary:
    domain_count: dict[str, URLDomainSummaryIndividual] = {}
    for url in url_observables:
        parsed_url = urlparse(url.value)
        if parsed_url.hostname not in domain_count:
            domain_count[parsed_url.hostname] = URLDomainSummaryIndividual(domain=parsed_url.hostname, count=1)
        else:
            domain_count[parsed_url.hostname].count += 1

    # Return a list of the URLDomainSummary objects sorted by their count (highest first) then the domain.
    # There isn't a built-in way to do this type of sort, so first sort by the secondary value (the domain).
    # Then sort by the primary value (the count).
    sorted_results = sorted(domain_count.values(), key=lambda x: x.domain)
    sorted_results = sorted(sorted_results, key=lambda x: x.count, reverse=True)

    return URLDomainSummary(domains=sorted_results, total=len(url_observables))
