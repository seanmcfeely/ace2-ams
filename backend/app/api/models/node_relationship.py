from pydantic import BaseModel, Field, UUID4
from uuid import uuid4

from api.models import type_str
from api.models.node import NodeRead
from api.models.node_relationship_type import NodeRelationshipTypeRead


class NodeRelationshipBase(BaseModel):
    """Represents a node relationship that can be applied to a node (typically an observable)."""

    node_uuid: UUID4 = Field(description="The UUID of the node")


class NodeRelationshipCreate(NodeRelationshipBase):
    related_node_uuid: UUID4 = Field(description="The UUID of the related node")

    type: type_str = Field(description="The type of the node relationship")

    uuid: UUID4 = Field(default_factory=uuid4, description="The UUID of the node relationship")


class NodeRelationshipRead(NodeRelationshipBase):
    uuid: UUID4 = Field(description="The UUID of the node relationship")

    related_node: NodeRead = Field(description="The related node")

    type: NodeRelationshipTypeRead = Field(description="The type of the node relationship")

    class Config:
        orm_mode = True
