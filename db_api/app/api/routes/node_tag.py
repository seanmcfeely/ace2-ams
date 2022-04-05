from fastapi import APIRouter, Depends, Request, Response
from fastapi_pagination.ext.sqlalchemy_future import paginate
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select
from uuid import UUID

from api_models.create import Create
from api_models.node_tag import NodeTagCreate, NodeTagRead, NodeTagUpdate
from api.routes import helpers
from db import crud
from db.database import get_db
from db.schemas.node_tag import NodeTag


router = APIRouter(
    prefix="/node/tag",
    tags=["Node Tag"],
)


#
# CREATE
#


def create_node_tag(
    create: NodeTagCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    obj: NodeTag = crud.create(obj=create, db_table=NodeTag, db=db)

    response.headers["Content-Location"] = request.url_for("get_node_tag", uuid=obj.uuid)

    return {"uuid": obj.uuid}


helpers.api_route_create(router, create_node_tag, response_model=Create)


#
# READ
#


def get_all_node_tags(db: Session = Depends(get_db)):
    return paginate(db, select(NodeTag).order_by(NodeTag.value))


def get_node_tag(uuid: UUID, db: Session = Depends(get_db)):
    return crud.read(uuid=uuid, db_table=NodeTag, db=db)


helpers.api_route_read_all(router, get_all_node_tags, NodeTagRead)
helpers.api_route_read(router, get_node_tag, NodeTagRead)


#
# UPDATE
#


def update_node_tag(
    uuid: UUID,
    node_tag: NodeTagUpdate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    crud.update(uuid=uuid, obj=node_tag, db_table=NodeTag, db=db)

    response.headers["Content-Location"] = request.url_for("get_node_tag", uuid=uuid)


helpers.api_route_update(router, update_node_tag)


#
# DELETE
#


def delete_node_tag(uuid: UUID, db: Session = Depends(get_db)):
    crud.delete(uuid=uuid, db_table=NodeTag, db=db)


helpers.api_route_delete(router, delete_node_tag)
