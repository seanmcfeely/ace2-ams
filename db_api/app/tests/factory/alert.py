import json

from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, Union
from uuid import UUID, uuid4

from api_models.alert import AlertCreate
from api_models.alert_disposition import AlertDispositionCreate
from api_models.alert_tool import AlertToolCreate
from api_models.alert_tool_instance import AlertToolInstanceCreate
from api_models.alert_type import AlertTypeCreate
from api_models.analysis import AnalysisCreate
from api_models.analysis_module_type import AnalysisModuleTypeCreate
from api_models.node_tag import NodeTagCreate
from api_models.node_threat_actor import NodeThreatActorCreate
from api_models.observable import ObservableCreate
from api_models.observable_type import ObservableTypeCreate
from api_models.queue import QueueCreate
from db import crud
from db.schemas.alert import Alert
from db.schemas.event import Event
from tests import factory


def create(
    db: Session,
    alert_queue: str = "external",
    alert_type: str = "test_type",
    alert_uuid: Optional[Union[str, UUID]] = None,
    disposition: Optional[str] = None,
    event: Optional[Event] = None,
    event_time: datetime = None,
    history_username: Optional[str] = None,
    insert_time: datetime = None,
    name: str = "Test Alert",
    observables: Optional[list[ObservableCreate]] = None,
    owner: Optional[str] = None,
    tags: Optional[list[str]] = None,
    threat_actors: Optional[list[str]] = None,
    threats: Optional[list[str]] = None,
    tool: str = "test_tool",
    tool_instance: str = "test_tool_instance",
    update_time: Optional[datetime] = None,
    updated_by_user: str = "analyst",
):
    diffs = []

    # Set default values
    if alert_uuid is None:
        alert_uuid = uuid4()

    if event_time is None:
        event_time = crud.helpers.utcnow()

    if insert_time is None:
        insert_time = crud.helpers.utcnow()

    if observables is None:
        observables = []

    if update_time is None:
        update_time = crud.helpers.utcnow()

    # Create the alert queue
    crud.queue.create(model=QueueCreate(value=alert_queue), db=db)

    # Create the alert type
    crud.alert_type.create(model=AlertTypeCreate(value=alert_type), db=db)

    # Create the tool and tool instance
    crud.alert_tool.create(model=AlertToolCreate(value=tool), db=db)
    crud.alert_tool_instance.create(model=AlertToolInstanceCreate(value=tool_instance), db=db)

    # Create the history user if one was given
    if history_username is not None:
        factory.user.create(username=history_username, db=db)

    # Create the owner user if one was given
    if owner is not None:
        factory.user.create(email=f"{owner}@{owner}.com", username=owner, db=db, alert_queue=alert_queue)
        diffs.append(crud.history.create_diff(field="owner", old=None, new=owner))

    # Create observable types for each observable that was given
    for observable in observables:
        crud.observable_type.create(model=ObservableTypeCreate(value=observable.type), db=db)

    alert = crud.alert.create(
        model=AlertCreate(
            event_time=event_time,
            insert_time=insert_time,
            history_username=history_username,
            name=name,
            owner=owner,
            queue=alert_queue,
            root_observables=observables,
            tool=tool,
            tool_instance=tool_instance,
            type=alert_type,
            uuid=alert_uuid,
        ),
        db=db,
    )

    if disposition:
        existing_dispositions = crud.alert_disposition.read_all(db=db)
        alert.disposition = crud.alert_disposition.create(
            model=AlertDispositionCreate(value=disposition, rank=len(existing_dispositions) + 1), db=db
        )
        alert.disposition_time = update_time
        alert.disposition_user = factory.user.create(username=updated_by_user, display_name=updated_by_user, db=db)
        diffs.append(crud.history.create_diff(field="disposition", old=None, new=disposition))

    if event:
        alert.event = event

    if tags:
        alert.tags = [crud.node_tag.create(model=NodeTagCreate(value=t), db=db) for t in tags]

    if threat_actors:
        alert.threat_actors = [
            crud.node_threat_actor.create(model=NodeThreatActorCreate(value=t)) for t in threat_actors
        ]

    if threats:
        alert.threats = [factory.node_threat.create(value=threat, db=db) for threat in threats]

    if history_username:
        if diffs and updated_by_user:
            crud.history.record_node_update_history(
                record_node=alert,
                action_by=factory.user.create(username=updated_by_user, db=db),
                action_time=update_time,
                diffs=diffs,
                db=db,
            )

    return alert


def create_from_json_file(db: Session, json_path: str, alert_name: str) -> Alert:
    def _create_observable(o, root_analysis_uuid: UUID) -> ObservableCreate:
        crud.observable_type.create(model=ObservableTypeCreate(value=o["type"]), db=db)
        observable_model = ObservableCreate(
            for_detection=o["for_detection"] if "for_detection" in o else False,
            root_analysis_uuid=root_analysis_uuid,
            tags=o["tags"] if "tags" in o else [],
            type=o["type"],
            value=o["value"],
        )
        if "analyses" in o:
            for a in o["analyses"]:
                analysis_module_type = crud.analysis_module_type.create(
                    AnalysisModuleTypeCreate(value=a["type"]), db=db
                )
                observable_model.analyses.append(
                    AnalysisCreate(
                        analysis_module_type_uuid=analysis_module_type.uuid,
                        child_observables=[
                            _create_observable(o=co, root_analysis_uuid=root_analysis_uuid) for co in a["observables"]
                        ]
                        if "observables" in a
                        else [],
                        details=json.dumps(a["details"]) if "details" in a else None,
                        parent_observable_uuid=observable_model.uuid,
                        root_analysis_uuid=root_analysis_uuid,
                        run_time=crud.helpers.utcnow(),
                    )
                )

        return observable_model

    def _replace_tokens(text: str, token: str, base_replacement_string: str) -> str:
        for i in range(text.count(token)):
            text = text.replace(token, f"{base_replacement_string}{i}", 1)

        return text

    with open(json_path) as f:
        text = f.read()

        text = text.replace("<ALERT_NAME>", alert_name)
        text = _replace_tokens(text, "<A_TYPE>", "a_type")
        text = _replace_tokens(text, "<O_TYPE>", "o_type")
        text = _replace_tokens(text, "<O_VALUE>", "o_value")
        text = _replace_tokens(text, "<TAG>", "tag")

        data = json.loads(text)

    if "alert_uuid" in data:
        alert_uuid = data["alert_uuid"]
        existing_alert = crud.alert.read_by_uuid(uuid=alert_uuid, db=db)
        if existing_alert is not None:
            return existing_alert
    else:
        alert_uuid = uuid4()

    disposition_user = None
    if "disposition_user" in data:
        disposition_user = data["disposition_user"]

    name = "Test Alert"
    if "name" in data:
        name = data["name"]

    owner = None
    if "owner" in data:
        owner = data["owner"]

    updated_by_user = "analyst"
    if disposition_user is not None:
        updated_by_user = disposition_user
    elif owner is not None:
        updated_by_user = owner

    alert = create(
        db=db,
        alert_uuid=alert_uuid,
        name=name,
        observables=[_create_observable(o=o, root_analysis_uuid=alert_uuid) for o in data["observables"]],
        owner=owner,
        updated_by_user=updated_by_user,
    )

    return alert


def stringify_alert_tree(alert_tree: dict):
    def _stringify_children(children: list[dict], depth=0, string=""):
        for child in children:
            duplicate = "" if child["first_appearance"] else " (Duplicate)"
            if child["node_type"] == "observable":
                string += f"{' '*depth}{child['type']['value']}: {child['value']}{duplicate}\n"
                if child["children"]:
                    string = _stringify_children(children=child["children"], depth=depth + 2, string=string)
            if child["node_type"] == "analysis":
                string += f"{' '*depth}{child['analysis_module_type']['value']}{duplicate}\n"
                if child["children"]:
                    string = _stringify_children(children=child["children"], depth=depth + 2, string=string)

        return string

    return _stringify_children(children=alert_tree["children"])
