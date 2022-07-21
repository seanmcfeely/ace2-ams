from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_pagination.ext.sqlalchemy_future import paginate
from sqlalchemy.orm import Session
from uuid import UUID

from api.routes import helpers
from api_models.history import ObservableHistoryRead
from api_models.observable import ObservableCreate, ObservableRead, ObservableUpdate, ObservableVersion
from db import crud
from db.database import get_db
from db.schemas.observable import Observable, ObservableHistory
from db.schemas.observable_type import ObservableType
from exceptions.db import UuidNotFoundInDatabase, ValueNotFoundInDatabase, VersionMismatch


router = APIRouter(
    prefix="/observable",
    tags=["Observable"],
)


#
# CREATE
#


def create_observables(
    observables: list[ObservableCreate],
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    for observable in observables:
        try:
            obj = crud.observable.create_or_read(model=observable, db=db)
        except (UuidNotFoundInDatabase, ValueNotFoundInDatabase) as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    db.commit()

    response.headers["Content-Location"] = request.url_for("get_observable", uuid=obj.uuid)


helpers.api_route_create(router, create_observables)


#
# READ
#


def get_all_observables(db: Session = Depends(get_db)):
    return paginate(conn=db, query=crud.observable.build_read_all_query())


def get_observable(uuid: UUID, db: Session = Depends(get_db)):
    try:
        return crud.observable.read_by_uuid(uuid=uuid, db=db)
    except UuidNotFoundInDatabase as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


def get_observable_history(uuid: UUID, db: Session = Depends(get_db)):
    return paginate(
        conn=db, query=crud.history.build_read_history_query(history_table=ObservableHistory, record_uuid=uuid)
    )


def get_observable_version(uuid: UUID, db: Session = Depends(get_db)):
    try:
        return crud.observable.read_by_uuid(uuid=uuid, db=db)
    except UuidNotFoundInDatabase as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


helpers.api_route_read_all(router, get_all_observables, ObservableRead)
helpers.api_route_read(router, get_observable, ObservableRead)
helpers.api_route_read_all(router, get_observable_history, ObservableHistoryRead, path="/{uuid}/history")
helpers.api_route_read(router, get_observable_version, ObservableVersion, path="/{uuid}/version")


#
# UPDATE
#


def update_observable(
    uuid: UUID,
    observable: ObservableUpdate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        if not crud.observable.update(uuid=uuid, model=observable, db=db):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to update observable {uuid}")
    except (UuidNotFoundInDatabase, ValueNotFoundInDatabase) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except VersionMismatch as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    db.commit()

    response.headers["Content-Location"] = request.url_for("get_observable", uuid=uuid)


helpers.api_route_update(router, update_observable)
