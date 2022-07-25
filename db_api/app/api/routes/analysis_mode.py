from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_pagination.ext.sqlalchemy_future import paginate
from sqlalchemy.orm import Session
from uuid import UUID

from api.routes import helpers
from api_models.analysis_mode import (
    AnalysisModeCreate,
    AnalysisModeRead,
    AnalysisModeUpdate,
)
from db import crud
from db.database import get_db
from db.schemas.analysis_mode import AnalysisMode
from exceptions.db import UuidNotFoundInDatabase


router = APIRouter(
    prefix="/analysis/mode",
    tags=["Analysis Mode"],
)


#
# CREATE
#


def create_analysis_mode(
    create: AnalysisModeCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    obj = crud.analysis_mode.create_or_read(model=create, db=db)
    db.commit()

    response.headers["Content-Location"] = request.url_for("get_analysis_mode", uuid=obj.uuid)


helpers.api_route_create(router, create_analysis_mode)


#
# READ
#


def get_all_analysis_modees(db: Session = Depends(get_db)):
    return paginate(conn=db, query=crud.analysis_mode.build_read_all_query())


def get_analysis_mode(uuid: UUID, db: Session = Depends(get_db)):
    try:
        return crud.analysis_mode.read_by_uuid(uuid=uuid, db=db)
    except UuidNotFoundInDatabase as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


helpers.api_route_read_all(router, get_all_analysis_modees, AnalysisModeRead)
helpers.api_route_read(router, get_analysis_mode, AnalysisModeRead)


#
# UPDATE
#


def update_analysis_mode(
    uuid: UUID,
    type: AnalysisModeUpdate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        if not crud.helpers.update(uuid=uuid, update_model=type, db_table=AnalysisMode, db=db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to update analysis mode {uuid}"
            )
    except UuidNotFoundInDatabase as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    db.commit()

    response.headers["Content-Location"] = request.url_for("get_analysis_mode", uuid=uuid)


helpers.api_route_update(router, update_analysis_mode)


#
# DELETE
#


def delete_analysis_mode(uuid: UUID, db: Session = Depends(get_db)):
    try:
        if not crud.helpers.delete(uuid=uuid, db_table=AnalysisMode, db=db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to delete analysis mode {uuid}"
            )
    except UuidNotFoundInDatabase as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    db.commit()


helpers.api_route_delete(router, delete_analysis_mode)
