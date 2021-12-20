from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from uuid import uuid4

from api.models import type_str
from api.models.node_comment import NodeCommentRead
from api.models.node_directive import NodeDirectiveRead
from api.models.node_tag import NodeTagRead
from api.models.node_threat import NodeThreatRead
from api.models.node_threat_actor import NodeThreatActorRead


class NodeTreeItemRead(BaseModel):
    parent_tree_uuid: Optional[UUID4] = Field(
        description="The node's parent leaf UUID if the node is inside a NodeTree"
    )

    tree_uuid: Optional[UUID4] = Field(description="The UUID of the leaf if this Node is inside a NodeTree")


class NodeBase(BaseModel):
    """Represents an individual node."""

    # TODO: Add a node_links_mapping table
    # links: Optional[List[UUID]] = Field(
    #     default_factory=list,
    #     description="The list of node UUIDs linked to this node. Nodes that are linked receive the same tags."
    # )

    # TODO: Add a node_relationships table and node_relationship_mapping table
    # relationships: Optional[Dict[type_str, List[UUID]]] = Field(
    #     default_factory=list,
    #     description="""A mapping of relationships between this node and other nodes. The key is the name of the
    #         relationship. The value for each key is a list of one or more node UUIDs related in this way."""
    # )

    version: UUID4 = Field(
        default_factory=uuid4,
        description="""A version string that automatically changes every time the node is modified. The version
            must match when updating.""",
    )


class NodeCreateDirectives(BaseModel):
    """Represents a Node that has directives."""

    directives: List[type_str] = Field(default_factory=list, description="A list of directives to add to the node")


class NodeCreateTags(BaseModel):
    """Represents a Node that has tags."""

    tags: List[type_str] = Field(default_factory=list, description="A list of tags to add to the node")


class NodeCreateThreatActors(BaseModel):
    """Represents a Node that has threat actors."""

    threat_actors: List[type_str] = Field(
        default_factory=list, description="A list of threat actors to add to the node"
    )


class NodeBaseThreats(BaseModel):
    """Represents a Node that has threats."""

    threats: List[type_str] = Field(default_factory=list, description="A list of threats to add to the node")


class NodeCreate(NodeBase):
    uuid: UUID4 = Field(default_factory=uuid4, description="The UUID of the node")


class NodeRead(NodeBase, NodeTreeItemRead):

    node_type: type_str = Field(description="The type of the Node")

    uuid: UUID4 = Field(description="The UUID of the node")

    class Config:
        orm_mode = True


class NodeReadComments(BaseModel):
    comments: List[NodeCommentRead] = Field(description="A list of comments added to the node")

    class Config:
        orm_mode = True


class NodeReadDirectives(BaseModel):
    directives: List[NodeDirectiveRead] = Field(description="A list of directives added to the node")

    class Config:
        orm_mode = True


class NodeReadTags(BaseModel):
    tags: List[NodeTagRead] = Field(description="A list of tags added to the node")

    class Config:
        orm_mode = True


class NodeReadThreatActors(BaseModel):
    threat_actors: List[NodeThreatActorRead] = Field(description="A list of threat actors added to the node")

    class Config:
        orm_mode = True


class NodeReadThreats(BaseModel):
    threats: List[NodeThreatRead] = Field(description="A list of threats added to the node")

    class Config:
        orm_mode = True


class NodeUpdate(NodeBase):
    # The version is optional when updating a Node since certain actions in the GUI do not need to care
    # about the version. However, if the version is given, the update will be rejected if it does not match.
    version: Optional[UUID4] = Field(
        description="""A version string that automatically changes every time the node is modified. If supplied,
        the version must match when updating.""",
    )


class NodeUpdateDirectives(BaseModel):
    directives: Optional[List[type_str]] = Field(description="A list of directives applied to the node")


class NodeUpdateTags(BaseModel):
    tags: Optional[List[type_str]] = Field(description="A list of tags to add to the node")


class NodeUpdateThreatActors(BaseModel):
    threat_actors: Optional[List[type_str]] = Field(description="A list of threat actors to add to the node")


class NodeUpdateThreats(BaseModel):
    threats: Optional[List[type_str]] = Field(description="A list of threats to add to the node")


class NodeTreeBase(BaseModel):
    """Represents a leaf in a Node tree."""

    node_uuid: UUID4 = Field(description="The UUID of the Node represented by the leaf")

    root_node_uuid: UUID4 = Field(
        description="""The Node UUID that contains the tree.
            For example, an alert UUID that contains a tree of analyses and observables."""
    )

    parent_tree_uuid: Optional[UUID4] = Field(description="The UUID of the parent leaf")

    class Config:
        orm_mode = True


class NodeTreeCreateWithNode(BaseModel):
    root_node_uuid: UUID4 = Field(
        description="""The node UUID that contains the tree.
            For example, an alert UUID that contains a tree of analyses and observables."""
    )

    parent_tree_uuid: Optional[UUID4] = Field(description="The UUID of the leaf in the tree that should be the parent")


class NodeTreeRead(BaseModel):
    root_node: NodeRead = Field(description="The root node of the tree. For example, this will often be an Alert.")

    leaves: List[NodeTreeBase] = Field(description="A list of the leaves that make up the tree")

    class Config:
        orm_mode = True


class NodeTreeUpdate(NodeTreeBase):
    root_node_uuid: Optional[UUID4] = Field(
        description="""The node UUID that contains the tree.
            For example, an alert UUID that contains a tree of analyses and observables."""
    )

    node_uuid: Optional[UUID4] = Field(description="The UUID of the Node represented by the leaf")
