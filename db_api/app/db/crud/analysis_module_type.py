from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select
from uuid import UUID

from api_models.analysis_module_type import AnalysisModuleTypeCreate, AnalysisModuleTypeUpdate
from api_models.metadata_directive import MetadataDirectiveCreate
from api_models.metadata_tag import MetadataTagCreate
from api_models.observable_type import ObservableTypeCreate
from db import crud
from db.schemas.analysis_module_type import AnalysisModuleType


def build_read_all_query() -> Select:
    return select(AnalysisModuleType).order_by(AnalysisModuleType.value, AnalysisModuleType.version)


def create_or_read(model: AnalysisModuleTypeCreate, db: Session) -> AnalysisModuleType:
    obj = AnalysisModuleType(
        cache_seconds=model.cache_seconds,
        description=model.description,
        extended_version=model.extended_version,
        manual=model.manual,
        observable_types=[
            crud.observable_type.create_or_read(model=ObservableTypeCreate(value=o), db=db)
            for o in set(model.observable_types)
        ],
        required_directives=[
            crud.metadata_directive.create_or_read(MetadataDirectiveCreate(value=d), db=db)
            for d in set(model.required_directives)
        ],
        required_tags=[
            crud.metadata_tag.create_or_read(model=MetadataTagCreate(value=t), db=db) for t in set(model.required_tags)
        ],
        uuid=model.uuid,
        value=model.value,
        version=model.version,
    )

    if crud.helpers.create(obj=obj, db=db):
        return obj

    return read_by_value_version(value=model.value, version=model.version, db=db)


def delete(uuid: UUID, db: Session) -> bool:
    return crud.helpers.delete(uuid=uuid, db_table=AnalysisModuleType, db=db)


def read_all(db: Session) -> list[AnalysisModuleType]:
    return db.execute(build_read_all_query()).scalars().all()


def read_by_uuid(uuid: UUID, db: Session) -> AnalysisModuleType:
    return crud.helpers.read_by_uuid(db_table=AnalysisModuleType, uuid=uuid, db=db)


def read_by_values_latest_version(values: list[str], db: Session) -> list[AnalysisModuleType]:
    if not values:
        return []

    # Get all of the analysis module types with the given values, sorting them by their values then versions
    analysis_module_types: list[AnalysisModuleType] = db.execute(
        select(AnalysisModuleType)
        .where(AnalysisModuleType.value.in_(values))
        .order_by(AnalysisModuleType.value.asc(), AnalysisModuleType.version.desc())
    ).scalars()

    # Loop through all the analysis module types and only return the latest version of each
    results: list[AnalysisModuleType] = []
    unique_analysis_module_type_values: set[str] = set()
    for analysis_module_type in analysis_module_types:
        if analysis_module_type.value not in unique_analysis_module_type_values:
            unique_analysis_module_type_values.add(analysis_module_type.value)
            results.append(analysis_module_type)

    return results


def read_by_value_version(value: str, version: str, db: Session) -> AnalysisModuleType:
    return (
        db.execute(
            select(AnalysisModuleType).where(AnalysisModuleType.value == value, AnalysisModuleType.version == version)
        )
        .scalars()
        .one()
    )


def update(uuid: UUID, model: AnalysisModuleTypeUpdate, db: Session) -> bool:
    obj = read_by_uuid(uuid=uuid, db=db)

    # Get the data that was given in the request and use it to update the database object
    update_data = model.dict(exclude_unset=True)

    with db.begin_nested():
        try:
            if "cache_seconds" in update_data:
                obj.cache_seconds = update_data["cache_seconds"]

            if "description" in update_data:
                obj.description = update_data["description"]

            if "extended_version" in update_data:
                obj.extended_version = update_data["extended_version"]

            if "manual" in update_data:
                obj.manual = update_data["manual"]

            if "observable_types" in update_data:
                obj.observable_types = crud.observable_type.read_by_values(
                    values=update_data["observable_types"], db=db
                )

            if "required_directives" in update_data:
                obj.required_directives = crud.metadata_directive.read_by_values(
                    values=update_data["required_directives"], db=db
                )

            if "required_tags" in update_data:
                obj.required_tags = crud.metadata_tag.read_by_values(values=update_data["required_tags"], db=db)

            if "value" in update_data:
                obj.value = update_data["value"]

            if "version" in update_data:
                obj.version = update_data["version"]

            db.flush()
            return True
        except IntegrityError:
            db.rollback()

    return False
