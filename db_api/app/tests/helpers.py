import json
import uuid

from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from typing import Dict, List, Optional, Union
from uuid import UUID

from core.auth import hash_password
from db import crud
from db.schemas.alert import Alert
from db.schemas.alert_disposition import AlertDisposition
from db.schemas.alert_tool import AlertTool
from db.schemas.alert_tool_instance import AlertToolInstance
from db.schemas.alert_type import AlertType
from db.schemas.analysis import Analysis
from db.schemas.analysis_module_type import AnalysisModuleType
from db.schemas.event import Event
from db.schemas.event_prevention_tool import EventPreventionTool
from db.schemas.event_remediation import EventRemediation
from db.schemas.event_risk_level import EventRiskLevel
from db.schemas.event_source import EventSource
from db.schemas.event_status import EventStatus
from db.schemas.event_type import EventType
from db.schemas.event_vector import EventVector
from db.schemas.node import Node
from db.schemas.node_comment import NodeComment
from db.schemas.node_detection_point import NodeDetectionPoint
from db.schemas.node_directive import NodeDirective
from db.schemas.node_relationship import NodeRelationship
from db.schemas.node_relationship_type import NodeRelationshipType
from db.schemas.node_tag import NodeTag
from db.schemas.node_threat import NodeThreat
from db.schemas.node_threat_actor import NodeThreatActor
from db.schemas.node_threat_type import NodeThreatType
from db.schemas.node_tree import NodeTree
from db.schemas.observable import Observable
from db.schemas.observable_type import ObservableType
from db.schemas.queue import Queue
from db.schemas.user import User, UserHistory
from db.schemas.user_role import UserRole


REALISTIC_ALERT_UUID = "02f8299b-2a24-400f-9751-7dd9164daf6a"


def _create_basic_object(value: str, db_table: DeclarativeMeta, db: Session):
    existing = crud.read_by_value(value=value, db_table=db_table, db=db, err_on_not_found=False)
    if existing:
        return existing

    obj = db_table(value=value)
    db.add(obj)
    crud.commit(db)
    return obj


def create_alert_disposition(value: str, db: Session, rank: Optional[int] = None) -> AlertDisposition:
    existing = crud.read_by_value(value=value, db_table=AlertDisposition, db=db, err_on_not_found=False)
    if existing:
        return existing

    if rank is None:
        existing_dispositions = crud.read_all(db_table=AlertDisposition, db=db)
        rank = len(existing_dispositions)

    disposition = AlertDisposition(value=value, rank=rank)
    db.add(disposition)
    crud.commit(db)
    return disposition


def create_alert_tool(value: str, db: Session) -> AlertTool:
    return _create_basic_object(db_table=AlertTool, value=value, db=db)


def create_alert_tool_instance(value: str, db: Session) -> AlertToolInstance:
    return _create_basic_object(db_table=AlertToolInstance, value=value, db=db)


def create_alert_type(value: str, db: Session) -> AlertType:
    return _create_basic_object(db_table=AlertType, value=value, db=db)


def create_alert(
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
    observables: Optional[List[dict]] = None,
    owner: Optional[str] = None,
    tags: Optional[List[str]] = None,
    threat_actors: Optional[List[str]] = None,
    threats: Optional[List[str]] = None,
    tool: str = "test_tool",
    tool_instance: str = "test_tool_instance",
    update_time: Optional[datetime] = None,
    updated_by_user: str = "analyst",
) -> NodeTree:
    diffs = []

    if update_time is None:
        update_time = datetime.utcnow()

    if alert_uuid is None:
        alert_uuid = uuid.uuid4()

    if event_time is None:
        event_time = datetime.utcnow()

    if insert_time is None:
        insert_time = datetime.utcnow()

    alert = Alert(
        event_time=event_time,
        insert_time=insert_time,
        name=name,
        queue=create_queue(value=alert_queue, db=db),
        tool=create_alert_tool(value=tool, db=db),
        tool_instance=create_alert_tool_instance(value=tool_instance, db=db),
        type=create_alert_type(value=alert_type, db=db),
        uuid=alert_uuid,
        version=uuid.uuid4(),
    )

    if disposition:
        alert.disposition = create_alert_disposition(value=disposition, db=db)
        alert.disposition_time = update_time
        alert.disposition_user = create_user(username=updated_by_user, display_name=updated_by_user, db=db)
        diffs.append(crud.create_diff(field="disposition", old=None, new=disposition))

    if event:
        alert.event = event

    if event_time:
        alert.event_time = event_time

    if insert_time:
        alert.insert_time = insert_time

    if owner:
        alert.owner = create_user(email=f"{owner}@{owner}.com", username=owner, db=db, alert_queue=alert_queue)
        diffs.append(crud.create_diff(field="owner", old=None, new=owner))

    if tags:
        alert.tags = [create_node_tag(value=tag, db=db) for tag in tags]

    if threat_actors:
        alert.threat_actors = [create_node_threat_actor(value=threat_actor, db=db) for threat_actor in threat_actors]

    if threats:
        alert.threats = [create_node_threat(value=threat, db=db) for threat in threats]

    db.add(alert)
    crud.commit(db)

    node_tree = crud.create_node_tree_leaf(root_node_uuid=alert.uuid, node_uuid=alert.uuid, db=db)

    if observables:
        for observable in observables:
            create_observable(
                type=observable["type"],
                value=observable["value"],
                parent_tree=node_tree,
                history_username=history_username,
                db=db,
            )

    crud.commit(db)

    if history_username:
        # Add an entry to the history table
        crud.record_node_create_history(
            record_node=alert,
            action_by=create_user(username=history_username, db=db),
            db=db,
        )

        if diffs and updated_by_user:
            crud.record_node_update_history(
                record_node=alert,
                action_by=create_user(username=updated_by_user, db=db),
                action_time=update_time,
                diffs=diffs,
                db=db,
            )

    return node_tree


def create_analysis(
    db: Session,
    parent_observable: Observable,
    parent_tree: NodeTree,
    amt_value: str = "test_module",
    amt_cache_seconds: int = 90,
    amt_description: Optional[str] = None,
    amt_extended_version: Optional[dict] = None,
    amt_manual: bool = False,
    amt_observable_types: List[str] = None,
    amt_required_directives: List[str] = None,
    amt_required_tags: List[str] = None,
    amt_version: str = "1.0.0",
    details: Optional[dict] = None,
    node_metadata: Optional[Dict[str, object]] = None,
    run_time: datetime = None,
) -> NodeTree:
    analysis_module_type = create_analysis_module_type(
        value=amt_value,
        cache_seconds=amt_cache_seconds,
        description=amt_description,
        extended_version=amt_extended_version,
        manual=amt_manual,
        observable_types=amt_observable_types,
        required_directives=amt_required_directives,
        required_tags=amt_required_tags,
        version=amt_version,
        db=db,
    )

    if run_time is None:
        run_time = datetime.utcnow()

    obj = Analysis(
        analysis_module_type=analysis_module_type,
        cached_until=datetime.utcnow() + timedelta(seconds=analysis_module_type.cache_seconds),
        details=details,
        parent_observable_uuid=parent_observable.uuid,
        run_time=run_time,
        uuid=uuid.uuid4(),
        version=uuid.uuid4(),
    )

    db.add(obj)
    crud.commit(db)

    node_tree = crud.create_node_tree_leaf(
        node_metadata=node_metadata,
        root_node_uuid=parent_tree.root_node_uuid,
        node_uuid=obj.uuid,
        parent_tree_uuid=parent_tree.uuid,
        db=db,
    )

    crud.commit(db)

    return node_tree


def create_analysis_module_type(
    value: str,
    db: Session,
    cache_seconds: int = 90,
    description: Optional[str] = None,
    extended_version: Optional[dict] = None,
    manual: bool = False,
    observable_types: List[str] = None,
    required_directives: List[str] = None,
    required_tags: List[str] = None,
    version: str = "1.0.0",
) -> AnalysisModuleType:
    existing = crud.read_by_value(value=value, db_table=AnalysisModuleType, db=db, err_on_not_found=False)
    if existing and existing.version == version:
        return existing

    if observable_types:
        observable_types = [create_observable_type(value=o, db=db) for o in observable_types]
    else:
        observable_types = []

    if required_directives:
        required_directives = [create_node_directive(value=d, db=db) for d in required_directives]
    else:
        required_directives = []

    if required_tags:
        required_tags = [create_node_tag(value=t, db=db) for t in required_tags]
    else:
        required_tags = []

    obj = AnalysisModuleType(
        value=value,
        cache_seconds=cache_seconds,
        description=description,
        extended_version=extended_version,
        manual=manual,
        observable_types=observable_types,
        required_directives=required_directives,
        required_tags=required_tags,
        uuid=uuid.uuid4(),
        version=version,
    )
    db.add(obj)
    crud.commit(db)
    return obj


def create_event(
    name: str,
    db: Session,
    alert_time: Optional[datetime] = None,
    contain_time: Optional[datetime] = None,
    created_time: Optional[datetime] = None,
    disposition_time: Optional[datetime] = None,
    history_username: Optional[str] = None,
    owner: Optional[str] = None,
    prevention_tools: Optional[List[str]] = None,
    queue: str = "external",
    remediation_time: Optional[datetime] = None,
    remediations: Optional[List[str]] = None,
    risk_level: Optional[str] = None,
    source: Optional[str] = None,
    status: str = "OPEN",
    tags: Optional[List[str]] = None,
    threat_actors: Optional[List[str]] = None,
    threats: Optional[List[str]] = None,
    type: Optional[str] = None,
    vectors: Optional[List[str]] = None,
) -> Event:
    obj = Event(
        name=name,
        queue=create_queue(value=queue, db=db),
        status=create_event_status(value=status, db=db),
        uuid=uuid.uuid4(),
        version=uuid.uuid4(),
    )

    if alert_time:
        obj.alert_time = alert_time

    if contain_time:
        obj.contain_time = contain_time

    if created_time:
        obj.creation_time = created_time

    if disposition_time:
        obj.disposition_time = disposition_time

    if owner:
        obj.owner = create_user(email=f"{owner}@{owner}.com", username=owner, db=db, event_queue=queue)

    if prevention_tools:
        obj.prevention_tools = [create_event_prevention_tool(value=p, db=db) for p in prevention_tools]

    if remediation_time:
        obj.remediation_time = remediation_time

    if remediations:
        obj.remediations = [create_event_remediation(value=r, db=db) for r in remediations]

    if risk_level:
        obj.risk_level = create_event_risk_level(value=risk_level, db=db)

    if source:
        obj.source = create_event_source(value=source, db=db)

    if tags:
        obj.tags = [create_node_tag(value=tag, db=db) for tag in tags]

    if threat_actors:
        obj.threat_actors = [create_node_threat_actor(value=threat_actor, db=db) for threat_actor in threat_actors]

    if threats:
        obj.threats = [create_node_threat(value=threat, db=db) for threat in threats]

    if type:
        obj.type = create_event_type(value=type, db=db)

    if vectors:
        obj.vectors = [create_event_vector(value=v, db=db) for v in vectors]

    db.add(obj)
    crud.commit(db)

    if history_username:
        crud.record_node_create_history(
            record_node=obj,
            action_by=create_user(username=history_username, db=db),
            db=db,
        )

    return obj


def create_event_prevention_tool(value: str, db: Session, queues: List[str] = None) -> EventPreventionTool:
    if queues is None:
        queues = ["external"]

    obj: EventPreventionTool = _create_basic_object(db_table=EventPreventionTool, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_event_remediation(value: str, db: Session, queues: List[str] = None) -> EventRemediation:
    if queues is None:
        queues = ["external"]

    obj: EventRemediation = _create_basic_object(db_table=EventRemediation, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_event_risk_level(value: str, db: Session, queues: List[str] = None) -> EventRiskLevel:
    if queues is None:
        queues = ["external"]

    obj: EventRiskLevel = _create_basic_object(db_table=EventRiskLevel, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_event_source(value: str, db: Session, queues: List[str] = None) -> EventSource:
    if queues is None:
        queues = ["external"]

    obj: EventSource = _create_basic_object(db_table=EventSource, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_event_status(value: str, db: Session, queues: List[str] = None) -> EventStatus:
    if queues is None:
        queues = ["external"]

    obj: EventStatus = _create_basic_object(db_table=EventStatus, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_event_type(value: str, db: Session, queues: List[str] = None) -> EventType:
    if queues is None:
        queues = ["external"]

    obj: EventType = _create_basic_object(db_table=EventType, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_event_vector(value: str, db: Session, queues: List[str] = None) -> EventVector:
    if queues is None:
        queues = ["external"]

    obj: EventVector = _create_basic_object(db_table=EventVector, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_node_comment(
    node: Node,
    username: str,
    value: str,
    db: Session,
    history_username: Optional[str] = None,
    insert_time: Optional[datetime] = None,
) -> NodeComment:
    if insert_time is None:
        insert_time = datetime.utcnow()

    user = create_user(username=username, db=db)

    obj = NodeComment(insert_time=insert_time, node_uuid=node.uuid, user=user, uuid=uuid.uuid4(), value=value)
    db.add(obj)
    crud.commit(db)

    if history_username:
        crud.record_node_update_history(
            record_node=node,
            action_by=create_user(username=history_username, display_name=history_username, db=db),
            action_time=insert_time,
            diffs=[crud.Diff(field="comments", added_to_list=[obj.value], removed_from_list=[])],
            db=db,
        )

    return obj


def create_node_detection_point(
    node: Node,
    value: str,
    db: Session,
    history_username: Optional[str] = None,
    insert_time: Optional[datetime] = None,
) -> NodeDetectionPoint:
    if insert_time is None:
        insert_time = datetime.utcnow()

    obj = NodeDetectionPoint(insert_time=insert_time, node_uuid=node.uuid, uuid=uuid.uuid4(), value=value)
    db.add(obj)
    crud.commit(db)

    if history_username:
        crud.record_node_update_history(
            record_node=node,
            action_by=create_user(username=history_username, display_name=history_username, db=db),
            action_time=insert_time,
            diffs=[crud.Diff(field="detection_points", added_to_list=[obj.value], removed_from_list=[])],
            db=db,
        )

    return obj


def create_node_directive(value: str, db: Session) -> NodeDirective:
    return _create_basic_object(db_table=NodeDirective, value=value, db=db)


def create_node_relationship(node: Node, related_node: Node, type: str, db: Session) -> NodeRelationship:
    obj = NodeRelationship(
        node_uuid=node.uuid, related_node=related_node, type=create_node_relationship_type(value=type, db=db)
    )
    db.add(obj)
    crud.commit(db)
    return obj


def create_node_relationship_type(value: str, db: Session) -> NodeRelationshipType:
    return _create_basic_object(db_table=NodeRelationshipType, value=value, db=db)


def create_node_tag(value: str, db: Session) -> NodeTag:
    return _create_basic_object(db_table=NodeTag, value=value, db=db)


def create_node_threat_actor(value: str, db: Session, queues: List[str] = None) -> NodeThreatActor:
    if queues is None:
        queues = ["external"]

    obj: NodeThreatActor = _create_basic_object(db_table=NodeThreatActor, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_node_threat(value: str, db: Session, queues: List[str] = None, types: List[str] = None) -> NodeThreat:
    existing = crud.read_by_value(value=value, db_table=NodeThreat, db=db, err_on_not_found=False)
    if existing:
        return existing

    if queues is None:
        queues = ["external"]

    if types is None:
        types = ["test_type"]

    obj = NodeThreat(
        value=value,
        queues=[create_queue(value=q, db=db) for q in queues],
        types=[create_node_threat_type(value=t, db=db, queues=queues) for t in types],
        uuid=uuid.uuid4(),
    )
    db.add(obj)
    crud.commit(db)
    return obj


def create_node_threat_type(value: str, db: Session, queues: List[str] = None) -> NodeThreatType:
    if queues is None:
        queues = ["external"]

    obj: NodeThreatType = _create_basic_object(db_table=NodeThreatType, value=value, db=db)
    obj.queues = [create_queue(value=queue, db=db) for queue in queues]

    return obj


def create_observable(
    type: str,
    value: str,
    parent_tree: NodeTree,
    db: Session,
    context: Optional[str] = None,
    directives: Optional[List[str]] = None,
    expires_on: Optional[datetime] = None,
    for_detection: bool = False,
    history_username: Optional[str] = None,
    node_metadata: Optional[Dict[str, object]] = None,
    redirection: Optional[Observable] = None,
    tags: Optional[List[str]] = None,
    threat_actors: Optional[List[str]] = None,
    threats: Optional[List[str]] = None,
    time: Optional[datetime] = None,
) -> NodeTree:
    if time is None:
        time = datetime.utcnow()

    obj = crud.read_observable(type=type, value=value, db=db)
    if not obj:
        obj = Observable(
            context=context,
            expires_on=expires_on,
            for_detection=for_detection,
            redirection=redirection,
            time=time,
            type=create_observable_type(value=type, db=db),
            uuid=uuid.uuid4(),
            value=value,
            version=uuid.uuid4(),
        )

        if directives:
            obj.directives = [create_node_directive(value=d, db=db) for d in directives]

        if tags:
            obj.tags = [create_node_tag(value=t, db=db) for t in tags]

        if threat_actors:
            obj.threat_actors = [create_node_threat_actor(value=threat_actor, db=db) for threat_actor in threat_actors]

        if threats:
            obj.threats = [create_node_threat(value=threat, db=db) for threat in threats]

        db.add(obj)
        crud.commit(db)

    node_tree = crud.create_node_tree_leaf(
        node_metadata=node_metadata,
        root_node_uuid=parent_tree.root_node_uuid,
        node_uuid=obj.uuid,
        parent_tree_uuid=parent_tree.uuid,
        db=db,
    )

    crud.commit(db)

    if history_username:
        crud.record_node_create_history(
            record_node=obj,
            action_by=create_user(username=history_username, db=db),
            db=db,
        )

    return node_tree


def create_observable_type(value: str, db: Session) -> ObservableType:
    return _create_basic_object(db_table=ObservableType, value=value, db=db)


def create_queue(value: str, db: Session) -> Queue:
    return _create_basic_object(db_table=Queue, value=value, db=db)


def create_user(
    username: str,
    db: Session,
    alert_queue: str = "external",
    display_name: str = "Analyst",
    email: Optional[str] = None,
    enabled: bool = True,
    event_queue: str = "external",
    history_username: Optional[str] = None,
    password: str = "asdfasdf",
    refresh_token: str = "asdf",
    roles: List[str] = None,
) -> User:
    existing = crud.read_user_by_username(username=username, db=db, err_on_not_found=False)
    if existing:
        return existing

    if email is None:
        email = f"{username}@test.com"

    if roles is None:
        roles = [create_user_role(value="test_role", db=db)]
    else:
        roles = [create_user_role(value=r, db=db) for r in roles]

    obj = User(
        default_alert_queue=create_queue(value=alert_queue, db=db),
        default_event_queue=create_queue(value=event_queue, db=db),
        display_name=display_name,
        email=email,
        enabled=enabled,
        password=hash_password(password),
        refresh_token=refresh_token,
        roles=roles,
        username=username,
        uuid=uuid.uuid4(),
    )
    db.add(obj)
    crud.commit(db)

    if history_username:
        crud.record_create_history(
            history_table=UserHistory,
            action_by=obj,
            record=obj,
            db=db,
        )

    return obj


def create_user_role(value: str, db: Session) -> UserRole:
    return _create_basic_object(db_table=UserRole, value=value, db=db)


def create_alert_from_json_file(db: Session, json_path: str, alert_name: str) -> NodeTree:
    def _create_analysis(a, parent_tree: NodeTree):
        details = None
        if "details" in a:
            details = a["details"]

        observable_types = None
        if "observable_types" in a:
            observable_types = a["observable_types"]

        node_metadata = None
        if "node_metadata" in a:
            node_metadata = a["node_metadata"]

        required_directives = None
        if "required_directives" in a:
            required_directives = a["required_directives"]

        required_tags = None
        if "required_tags" in a:
            required_tags = a["required_tags"]

        leaf = create_analysis(
            db=db,
            node_metadata=node_metadata,
            parent_tree=parent_tree,
            amt_value=a["type"],
            amt_observable_types=observable_types,
            amt_required_directives=required_directives,
            amt_required_tags=required_tags,
            details=details,
        )

        if "observables" in a:
            for observable in a["observables"]:
                _create_observable(o=observable, parent_tree=leaf)

    def _create_observable(o, parent_tree: NodeTree):
        node_metadata = None
        if "node_metadata" in o:
            node_metadata = o["node_metadata"]

        tags = None
        if "tags" in o:
            tags = o["tags"]

        for_detection = False
        if "for_detection" in o:
            for_detection = o["for_detection"]

        leaf = create_observable(
            db=db,
            node_metadata=node_metadata,
            parent_tree=parent_tree,
            type=o["type"],
            value=o["value"],
            for_detection=for_detection,
            tags=tags,
        )

        if "observable_relationships" in o:
            for relationship in o["observable_relationships"]:
                related_observable = crud.read_observable(
                    type=relationship["o_type"], value=relationship["o_value"], db=db
                )

                create_node_relationship(
                    node=leaf.node, related_node=related_observable, type=relationship["type"], db=db
                )

        if "analyses" in o:
            for analysis in o["analyses"]:
                _create_analysis(a=analysis, parent_tree=leaf)

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

    alert_uuid = None
    if "alert_uuid" in data:
        alert_uuid = data["alert_uuid"]
        existing = read_node_tree_leaf(root_node_uuid=alert_uuid, node_uuid=alert_uuid, db=db)
        if existing:
            return existing

    disposition_user = None
    if "disposition_user" in data:
        disposition_user = data["disposition_user"]

    name = "Test Alert"
    if "name" in data:
        name = data["name"]

    owner = None
    if "owner" in data:
        owner = data["owner"]

    node_tree = create_alert(
        db=db,
        alert_uuid=alert_uuid,
        name=name,
        owner=owner,
        updated_by_user=disposition_user,
    )

    for observable in data["observables"]:
        _create_observable(o=observable, parent_tree=node_tree)

    return node_tree


def read_node_tree_leaf(root_node_uuid: UUID, node_uuid: UUID, db: Session) -> Optional[NodeTree]:
    return (
        db.execute(select(NodeTree).where(NodeTree.root_node_uuid == root_node_uuid, NodeTree.node_uuid == node_uuid))
        .scalars()
        .one_or_none()
    )
