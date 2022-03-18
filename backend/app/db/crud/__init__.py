import json

from dataclasses import dataclass
from datetime import datetime, timezone
from fastapi import HTTPException, status
from fastapi_pagination.ext.sqlalchemy_future import paginate
from pydantic import BaseModel
from pydantic.types import UUID4
from sqlalchemy import delete as sql_delete, select, update as sql_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import undefer, Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import join
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from api.models.alert import AlertRead
from api.models.event import EventRead
from api.models.node import NodeRead, NodeTreeMetadata
from api.models.observable import ObservableRead
from core.auth import verify_password
from db.schemas.alert import Alert, AlertHistory
from db.schemas.event import Event, EventHistory
from db.schemas.node import Node
from db.schemas.node_tree import NodeTree
from db.schemas.observable import Observable, ObservableHistory
from db.schemas.observable_type import ObservableType
from db.schemas.user import User


#
# HISTORY
#


@dataclass
class Diff:
    field: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    added_to_list: Optional[list[str]] = None
    removed_from_list: Optional[list[str]] = None


def create_diff(
    field: str,
    old: Union[None, str, list[str], datetime, UUID] = None,
    new: Union[None, str, list[str], datetime, UUID] = None,
) -> Optional[Diff]:
    # Convert datetime objects to UTC strings
    if isinstance(old, datetime):
        old = old.astimezone(timezone.utc).isoformat()
    if isinstance(new, datetime):
        new = new.astimezone(timezone.utc).isoformat()

    # Convert UUID objects to strings
    if isinstance(old, UUID):
        old = str(old)
    if isinstance(new, UUID):
        new = str(new)

    if isinstance(old, list) and isinstance(new, list):
        added = sorted(set([x for x in new if x not in old]))
        removed = sorted(set([x for x in old if x not in new]))
        return Diff(field=field, added_to_list=added, removed_from_list=removed)

    return Diff(field=field, old_value=old, new_value=new)


def read_history_records(history_table: DeclarativeMeta, record_uuid: UUID, db: Session):
    """Returns a paginated list of records from the given history table that involve the given record UUID."""

    query = (
        select(history_table).where(history_table.record_uuid == record_uuid).order_by(history_table.action_time.asc())
    )

    return paginate(db, query)


def record_create_history(
    history_table: DeclarativeMeta,
    action_by: User,
    record_read_model: BaseModel,
    record_table: DeclarativeMeta,
    record_uuid: UUID,
    db: Session,
):
    db_obj = read(uuid=record_uuid, db_table=record_table, db=db)
    snapshot = json.loads(record_read_model(**db_obj.__dict__).json())
    db.add(
        history_table(
            action="CREATE",
            action_by=action_by,
            action_time=datetime.utcnow(),
            record_uuid=record_uuid,
            snapshot=snapshot,
        )
    )
    commit(db)


def record_node_update_history(record_node: Node, action_by: User, diff: Diff, db: Session):
    if record_node.node_type == "alert":
        record_update_histories(
            history_table=AlertHistory,
            action_by=action_by,
            record_read_model=AlertRead,
            record_table=Alert,
            record_uuid=record_node.uuid,
            diffs=[diff],
            db=db,
        )
    elif record_node.node_type == "event":
        record_update_histories(
            history_table=EventHistory,
            action_by=action_by,
            record_read_model=EventRead,
            record_table=Event,
            record_uuid=record_node.uuid,
            diffs=[diff],
            db=db,
        )
    elif record_node.node_type == "observable":
        record_update_histories(
            history_table=ObservableHistory,
            action_by=action_by,
            record_read_model=ObservableRead,
            record_table=Observable,
            record_uuid=record_node.uuid,
            diffs=[diff],
            db=db,
        )


def record_update_histories(
    history_table: DeclarativeMeta,
    action_by: User,
    record_read_model: BaseModel,
    record_table: DeclarativeMeta,
    record_uuid: UUID,
    diffs: list[Diff],
    db: Session,
    action_time: Optional[datetime] = None,
):
    db_obj = read(uuid=record_uuid, db_table=record_table, db=db)
    snapshot = json.loads(record_read_model(**db_obj.__dict__).json())

    if action_time is None:
        action_time = datetime.utcnow()

    for diff in diffs:
        if diff:
            db.add(
                history_table(
                    action="UPDATE",
                    action_by=action_by,
                    action_time=action_time,
                    record_uuid=record_uuid,
                    field=diff.field,
                    diff={
                        "old_value": diff.old_value,
                        "new_value": diff.new_value,
                        "added_to_list": diff.added_to_list,
                        "removed_from_list": diff.removed_from_list,
                    },
                    snapshot=snapshot,
                )
            )

    commit(db)


#
# AUTH
#


def auth(username: str, password: str, db: Session) -> Optional[User]:
    """Returns the user from the database if the given username and password are valid."""

    user = db.execute(select(User).where(User.username == username)).scalars().one_or_none()

    if user and verify_password(password, user.password):
        return user

    return None


#
# CREATE
#


def create(obj: BaseModel, db_table: DeclarativeMeta, db: Session, exclude: Optional[List[str]] = None) -> Any:
    """Creates a new object in the given database table. Returns the new object's UUID.
    Designed to be called only by the API since it raises an HTTPException."""

    if exclude:
        new_obj = db_table(**obj.dict(exclude=set(exclude)))
    else:
        new_obj = db_table(**obj.dict())
    db.add(new_obj)
    commit(db)
    return new_obj


def create_node_tree_leaf(
    root_node_uuid: UUID,
    node_uuid: UUID,
    db: Session,
    node_metadata: Optional[Union[NodeTreeMetadata, Dict[str, object]]] = None,
    parent_tree_uuid: Optional[UUID] = None,
) -> NodeTree:
    """Creates an entry in the NodeTree table."""

    root_node: Node = read(uuid=root_node_uuid, db_table=Node, db=db)

    leaf = NodeTree()
    leaf.root_node_uuid = root_node.uuid
    leaf.node_uuid = node_uuid

    if isinstance(node_metadata, NodeTreeMetadata):
        node_metadata = node_metadata.dict()

    leaf.node_metadata = node_metadata

    if parent_tree_uuid:
        parent_tree: NodeTree = read(uuid=parent_tree_uuid, db_table=NodeTree, db=db)
        leaf.parent_tree_uuid = parent_tree.uuid

        # Update the parent node's version
        parent_node: Node = read(uuid=parent_tree.node_uuid, db_table=Node, db=db)
        parent_node.version = uuid4()

    # Update the root node's version
    root_node.version = uuid4()

    db.add(leaf)

    return leaf


#
# READ
#


def read_all(db_table: DeclarativeMeta, db: Session) -> List:
    """Returns all objects from the given database table."""

    return db.execute(select(db_table)).scalars().all()


def read(uuid: UUID, db_table: DeclarativeMeta, db: Session, err_on_not_found: bool = True, undefer_column: str = None):
    """Returns the single object with the given UUID if it exists, otherwise raises HTTPException.
    Designed to be called only by the API since it raises an HTTPException."""

    query = select(db_table).where(db_table.uuid == uuid)

    if undefer_column:
        query = query.options(undefer(undefer_column))

    result = db.execute(query).scalars().one_or_none()

    if result is None:
        if err_on_not_found:
            raise HTTPException(status_code=404, detail=f"UUID {uuid} does not exist in {db_table}.")

    return result


def read_by_uuids(uuids: List[UUID], db_table: DeclarativeMeta, db: Session):
    """Returns a list of objects with the given UUIDs. Designed to be called only by the API
    since it raises an HTTPException."""

    # Return without performing a database query if the list of values is empty
    if uuids == []:
        return uuids

    # Only search the database for unique UUIDs
    uuids = list(set(uuids))

    resources = db.execute(select(db_table).where(db_table.uuid.in_(uuids))).scalars().all()

    for uuid in uuids:
        if not any(uuid == r.uuid for r in resources):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The {uuid} {db_table} does not exist",
            )

    return resources


def read_observable(type: str, value: str, db: Session) -> Union[Observable, None]:
    """Returns the Observable with the given type and value if it exists."""

    return (
        db.execute(
            select(Observable).join(ObservableType).where(ObservableType.value == type, Observable.value == value)
        )
        .scalars()
        .one_or_none()
    )


def read_user_by_username(username: str, db: Session, err_on_not_found: bool = True) -> Optional[User]:
    """Returns the User with the given username if it exists. Designed to be called only
    by the API since it raises an HTTPException."""

    if not username:
        return None

    try:
        return db.execute(select(User).where(User.username == username)).scalars().one()
    except NoResultFound:
        if err_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The user {username} does not exist",
            )


def read_by_value(value: str, db_table: DeclarativeMeta, db: Session, err_on_not_found: bool = True):
    """Returns an object from the given database table with the given value.
    Designed to be called only by the API since it raises an HTTPException."""

    # Return early if the value is None
    if not value:
        return None

    try:
        result = db.execute(select(db_table).where(db_table.value == value)).scalars().one()
        return result
    # MultipleResultsFound exception is not caught since each database table that has a
    # value column should be configured to have that column be unique.
    except NoResultFound:
        if err_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The {value} {db_table} does not exist",
            )


def read_by_values(values: List[str], db_table: DeclarativeMeta, db: Session):
    """Returns a list of objects from the given database table with the given values.
    Designed to be called only by the API since it raises an HTTPException."""

    # Return without performing a database query if the list of values is empty or None
    if not values:
        return []

    # Only search the database for unique values
    values = list(set(values))

    resources = db.execute(select(db_table).where(db_table.value.in_(values))).scalars().all()

    for value in values:
        if not any(value == r.value for r in resources):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The {value} {db_table} does not exist",
            )

    return resources


def read_node_tree(root_node_uuid: UUID, db: Session) -> dict:
    """Returns a list of Node objects that comprise a Node Tree. The returned objects
    are manually serialized into their Pydantic models since Pydantic cannot handle
    returning a list of multiple types of objects in this case."""

    # While we can query the Node table and get back a list of various types of objects (Analysis, Observable, etc)
    # due to the polymorphic loading, Pydantic cannot handle returning multiple types of similar objects in a list.
    # If you try to use a Union of types in the response model, it will try to match the object with the first type
    # in the Union that fits. And since all of the Node child objects share certain properties, there is no way for
    # Pydantic to properly match the types.
    #
    # It's not an ideal solution, but the only way I've found around this is to query the database for all the Node
    # objects and then manually check their types to serialize them into their correct Pydantic models. Then the
    # response model for this API endpoint is simply a "dict" instead of a more specific type.
    #
    # Source: https://github.com/samuelcolvin/pydantic/issues/514#issuecomment-491298181

    node_tree_and_nodes: List[Tuple[NodeTree, Node]] = (
        db.execute(
            select([NodeTree, Node])
            .select_from(join(NodeTree, Node, NodeTree.node_uuid == Node.uuid))
            .where(NodeTree.root_node_uuid == root_node_uuid)
        )
        .unique()
        .fetchall()
    )

    if not node_tree_and_nodes:
        raise HTTPException(status_code=404, detail=f"Tree for {root_node_uuid} does not exist.")

    node_tree_nodes = []
    for leaf, node in node_tree_and_nodes:
        # Inject the tree information into the Node
        node.node_metadata = leaf.node_metadata
        node.tree_uuid = leaf.uuid
        node.parent_tree_uuid = leaf.parent_tree_uuid

        # Serialize the database objects into their correct Pydantic models
        node_tree_nodes.append(node.serialize_for_node_tree())

    return unflatten_node_tree(node_tree_nodes)


def read_node_tree_nodes(node_type: str, root_node_uuids: list[UUID], db: Session) -> list[dict]:
    """Returns a list of Node objects of the given type that are in the given NodeTrees.
    The returned objects are manually serialized into their Pydantic models since Pydantic
    cannot handle returning a list of multiple types of objects in this case."""

    nodes: List[Node] = (
        db.execute(
            select(Node)
            .select_from(join(NodeTree, Node, NodeTree.node_uuid == Node.uuid))
            .where(NodeTree.root_node_uuid.in_(root_node_uuids), Node.node_type == node_type)
        )
        .scalars()
        .unique()
        .fetchall()
    )

    if not nodes:
        raise HTTPException(status_code=404, detail=f"No Nodes of type {node_type} in trees {root_node_uuids}")

    return [node.__dict__ for node in nodes]


def unflatten_node_tree(node_tree_nodes: List[NodeRead]) -> dict:
    """Takes a flat list of nodes from a NodeTree after they've been serialized into
    their Pydantic models and converts it into a nested structure.

    Adapted from: https://www.npmjs.com/package/performant-array-to-tree"""

    root_node = {}

    # Used to store the already processed nodes where the node's UUID is the key
    lookup: Dict[UUID4, dict] = {}

    for node in node_tree_nodes:
        # If this node is not already in the lookup table, add a preliminary item for it
        if node.tree_uuid not in lookup:
            lookup[node.tree_uuid] = {"children": []}

        # Add the node's data to the item in the lookup table. Remember the nodes in the
        # list are Pydantic model objects, so to update the dictionary in the lookup table,
        # we have to work with the Pydantic object's dictionary as well.
        #
        # Also, exclude_unset is used because the Node objects out of the database do not
        # actually have a "children" field, and since its Pydantic model uses an empty list
        # as the default_factory, updating the item in the lookup table would overwrite
        # the children key with an empty list.
        lookup[node.tree_uuid].update(node.dict(exclude_unset=True))

        # If the node does not have a parent, add it as the root node
        if not node.parent_tree_uuid:
            root_node = lookup[node.tree_uuid]
        else:
            # If the parent is not already in the lookup table, add a preliminary item for it
            if node.parent_tree_uuid not in lookup:
                lookup[node.parent_tree_uuid] = {"children": []}

            # Add the node to its parent
            lookup[node.parent_tree_uuid]["children"].append(lookup[node.tree_uuid])

    # Now that the tree is unflattened, we need to walk it to mark which of the Nodes have
    # already appeared in the tree. This is useful for when you might not want to display or
    # process a Node in the tree if it is a duplicate.
    #
    # Adapted from: https://www.geeksforgeeks.org/preorder-traversal-of-n-ary-tree-without-recursion/
    unique_uuids = []
    unvisited = [{"uuid": "root", "children": [root_node]}]

    while unvisited:
        current = unvisited.pop(0)

        if current["uuid"] in unique_uuids:
            current["first_appearance"] = False
        else:
            current["first_appearance"] = True
            unique_uuids.append(current["uuid"])

        for idx in range(len(current["children"]) - 1, -1, -1):
            unvisited.insert(0, current["children"][idx])

    return root_node


#
# UPDATE
#


def update(uuid: UUID, obj: BaseModel, db_table: DeclarativeMeta, db: Session):
    """Updates the object with the given UUID in the database.
    Designed to be called only by the API since it raises an HTTPException."""

    # Try to perform the update
    try:
        result = db.execute(
            sql_update(db_table)
            .where(db_table.uuid == uuid)
            .values(
                # exclude_unset is needed for update routes so that any values in the Pydantic model
                # that are not being updated are not set to None. Instead they will be removed from the dict.
                **obj.dict(exclude_unset=True)
            )
        )

        # Verify a row was actually updated
        if result.rowcount != 1:
            raise HTTPException(status_code=404, detail=f"UUID {uuid} does not exist.")

        commit(db)

    # An IntegrityError will happen if value already exists or was set to None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Got an IntegrityError while updating UUID {uuid}.",
        )


#
# DELETE
#


def delete(uuid: UUID, db_table: DeclarativeMeta, db: Session):
    """Deletes the object with the given UUID from the database.
    Designed to be called only by the API since it raises an HTTPException."""

    # Make sure the resource exists so that better error messages can be returned. The read
    # function will raise an exception and return a 404 status if the resource does not exist.
    result = read(uuid=uuid, db_table=db_table, db=db)

    # NOTE: This will need to be updated to account for foreign key constraint errors.
    result = db.execute(sql_delete(db_table).where(db_table.uuid == uuid))

    # If the rowcount is not 1, it means the resource could not be deleted. Because we know at
    # this point that the resource actually exists, it could not be deleted due to a foreign
    # key constraint.
    if result.rowcount != 1:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to delete {db_table} UUID {uuid} due to a foreign key constraint.",
        )

    commit(db)


#
# COMMIT
#


def commit(db: Session):
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Got an IntegrityError while committing the database session: {e}",
        )
