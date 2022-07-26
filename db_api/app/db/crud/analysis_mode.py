from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select
from uuid import UUID

from api_models.analysis_mode import AnalysisModeCreate, AnalysisModeUpdate
from db import crud
from db.schemas.analysis_mode import AnalysisMode


def build_read_all_query() -> Select:
    return select(AnalysisMode).order_by(AnalysisMode.value)


def create_or_read(model: AnalysisModeCreate, db: Session) -> AnalysisMode:
    obj = AnalysisMode(
        analysis_module_types=crud.analysis_module_type.read_by_values_latest_version(
            values=model.analysis_module_types, db=db
        ),
        description=model.description,
        uuid=model.uuid,
        value=model.value,
    )

    if crud.helpers.create(obj=obj, db=db):
        return obj

    return read_by_value(value=model.value, db=db)


def delete(uuid: UUID, db: Session) -> bool:
    return crud.helpers.delete(uuid=uuid, db_table=AnalysisMode, db=db)


def read_all(db: Session) -> list[AnalysisMode]:
    return db.execute(build_read_all_query()).scalars().all()


def read_by_uuid(uuid: UUID, db: Session) -> AnalysisMode:
    return crud.helpers.read_by_uuid(db_table=AnalysisMode, uuid=uuid, db=db)


def read_by_value(value: str, db: Session) -> AnalysisMode:
    return crud.helpers.read_by_value(db_table=AnalysisMode, value=value, db=db)


def update(uuid: UUID, model: AnalysisModeUpdate, db: Session) -> bool:
    obj = read_by_uuid(uuid=uuid, db=db)

    # Get the data that was given in the request and use it to update the database object
    update_data = model.dict(exclude_unset=True)

    with db.begin_nested():
        try:
            if "analysis_module_types" in update_data:
                obj.analysis_module_types = crud.analysis_module_type.read_by_values_latest_version(
                    values=update_data["analysis_module_types"], db=db
                )

            if "description" in update_data:
                obj.description = update_data["description"]

            if "value" in update_data:
                obj.value = update_data["value"]

            db.flush()
            return True
        except IntegrityError:
            db.rollback()

    return False
