import json

from fastapi import APIRouter, Request, Response
from uuid import UUID

from api import db_api
from api.routes import helpers
from api_models.observable import ObservableRead, ObservableUpdate


router = APIRouter(
    prefix="/observable",
    tags=["Observable"],
)


#
# READ
#


def get_observable(uuid: UUID):
    return db_api.get(path=f"/observable/{uuid}")


helpers.api_route_read(router, get_observable, ObservableRead)


#
# UPDATE
#


def update_observable(
    uuid: UUID,
    observable: ObservableUpdate,
    request: Request,
    response: Response,
):
    db_api.patch(path=f"/observable/{uuid}", payload=json.loads(observable.json(exclude_unset=True)))

    response.headers["Content-Location"] = request.url_for("get_observable", uuid=uuid)


helpers.api_route_update(router, update_observable)
