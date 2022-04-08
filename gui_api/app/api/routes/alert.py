import json

from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, Response
from typing import List, Optional
from uuid import UUID

from api import db_api
from api.routes import helpers
from api_models.alert import AlertCreate, AlertRead, AlertUpdateMultiple
from api_models.history import AlertHistoryRead
from core.auth import validate_access_token


router = APIRouter(
    prefix="/alert",
    tags=["Alert"],
)


#
# CREATE
#


def create_alert(
    alert: AlertCreate,
    request: Request,
    response: Response,
    claims: dict = Depends(validate_access_token),
):
    result = db_api.post(path=f"/alert/?history_username={claims['sub']}", payload=json.loads(alert.json()))

    response.headers["Content-Location"] = request.url_for("get_alert", uuid=result["uuid"])


helpers.api_route_create(router, create_alert)


#
# READ
#


def get_all_alerts(
    limit: Optional[int] = Query(50, le=100),
    offset: Optional[int] = Query(0),
    disposition: Optional[str] = None,
    disposition_user: Optional[str] = None,
    dispositioned_after: Optional[datetime] = None,
    dispositioned_before: Optional[datetime] = None,
    event_uuid: Optional[UUID] = None,
    event_time_after: Optional[datetime] = None,
    event_time_before: Optional[datetime] = None,
    insert_time_after: Optional[datetime] = None,
    insert_time_before: Optional[datetime] = None,
    name: Optional[str] = None,
    observable: Optional[str] = Query(None, regex="^[\w\-]+\|.+$"),  # type|value
    observable_types: Optional[str] = None,
    observable_value: Optional[str] = None,
    owner: Optional[str] = None,
    queue: Optional[str] = None,
    sort: Optional[str] = Query(
        None,
        regex=""
        "^("
        "(disposition)|"
        "(disposition_time)|"
        "(disposition_user)|"
        "(event_time)|"
        "(insert_time)|"
        "(name)|"
        "(owner)|"
        "(queue)|"
        "(type)"
        ")\|"
        "("
        "(asc)|"
        "(desc)"
        ")$",
    ),  # Example: event_time|desc,
    tags: Optional[str] = None,
    threat_actors: Optional[str] = None,
    threats: Optional[str] = None,
    tool: Optional[str] = None,
    tool_instance: Optional[str] = None,
    type: Optional[str] = None,
):
    query_params = f"?limit={limit}&offset={offset}"

    if disposition:
        query_params += f"&disposition={disposition}"

    if disposition_user:
        query_params += f"&disposition_user={disposition_user}"

    if dispositioned_after:
        query_params += f"&dispositioned_after={dispositioned_after}"

    if dispositioned_before:
        query_params += f"&dispositioned_before={dispositioned_before}"

    if event_time_after:
        query_params += f"&event_time_after={event_time_after}"

    if event_time_before:
        query_params += f"&event_time_before={event_time_before}"

    if event_uuid:
        query_params += f"&event_uuid={event_uuid}"

    if insert_time_after:
        query_params += f"&insert_time_after={insert_time_after}"

    if insert_time_before:
        query_params += f"&insert_time_before={insert_time_before}"

    if name:
        query_params += f"&name={name}"

    if observable:
        query_params += f"&observable={observable}"

    if observable_types:
        query_params += f"&observable_types={observable_types}"

    if observable_value:
        query_params += f"&observable_value={observable_value}"

    if owner:
        query_params += f"&owner={owner}"

    if queue:
        query_params += f"&queue={queue}"

    if tags:
        query_params += f"&tags={tags}"

    if threat_actors:
        query_params += f"&threat_actors={threat_actors}"

    if threats:
        query_params += f"&threats={threats}"

    if tool:
        query_params += f"&tool={tool}"

    if tool_instance:
        query_params += f"&tool_instance={tool_instance}"

    if type:
        query_params += f"&type={type}"

    if sort:
        query_params += f"&sort={sort}"

    return db_api.get(path=f"/alert/{query_params}")


def get_alert(uuid: UUID):
    return db_api.get(path=f"/alert/{uuid}")


def get_alert_history(uuid: UUID, limit: Optional[int] = Query(50, le=100), offset: Optional[int] = Query(0)):
    query_params = f"?limit={limit}&offset={offset}"
    return db_api.get(f"/alert/{uuid}/history{query_params}")


helpers.api_route_read_all(router, get_all_alerts, AlertRead)
helpers.api_route_read(router, get_alert, dict)
helpers.api_route_read_all(router, get_alert_history, AlertHistoryRead, path="/{uuid}/history")


#
# UPDATE
#


def update_alerts(
    alerts: List[AlertUpdateMultiple],
    request: Request,
    response: Response,
    claims: dict = Depends(validate_access_token),
):
    db_api.patch(
        path=f"/alert/?history_username={claims['sub']}",
        payload=[json.loads(a.json(exclude_unset=True)) for a in alerts],
    )

    response.headers["Content-Location"] = request.url_for("get_alert", uuid=alerts[-1].uuid)


helpers.api_route_update(router, update_alerts, path="/")
