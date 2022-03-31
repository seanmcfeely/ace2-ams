from pydantic import Field, Json, UUID4
from typing import List, Optional
from uuid import uuid4

from api.models import type_str
from api.models.analysis_module_type import AnalysisModuleTypeNodeTreeRead, AnalysisModuleTypeRead
from api.models.node import NodeBase, NodeCreate, NodeRead, NodeTreeCreateWithNode, NodeTreeItemRead, NodeUpdate
from api.models.node_detection_point import NodeDetectionPointRead


class AnalysisBase(NodeBase):
    """Represents an individual analysis that was performed."""

    analysis_module_type: Optional[UUID4] = Field(
        description="""The UUID of the analysis module type that was used to perform this analysis. This can be NULL in
            the case of manually created alerts."""
    )

    details: Optional[Json] = Field(description="A JSON representation of the details produced by the analysis")

    error_message: Optional[type_str] = Field(description="An optional error message that occurred during analysis")

    stack_trace: Optional[type_str] = Field(description="An optional stack trace that occurred during analysis")

    summary: Optional[type_str] = Field(description="A short summary/description of what this analysis did or found")


class AnalysisCreate(NodeCreate, AnalysisBase):
    node_tree: NodeTreeCreateWithNode = Field(description="This defines where in a Node Tree this analysis fits")

    uuid: UUID4 = Field(default_factory=uuid4, description="The UUID of the analysis")


class AnalysisNodeTreeRead(NodeTreeItemRead):
    """Model used to control which information for an Analysis is displayed when getting an alert tree"""

    analysis_module_type: Optional[AnalysisModuleTypeNodeTreeRead] = Field(
        description="The analysis module type that was used to perform this analysis"
    )

    uuid: UUID4 = Field(description="The UUID of the analysis")

    class Config:
        orm_mode = True


class AnalysisRead(NodeRead, AnalysisBase):
    analysis_module_type: Optional[AnalysisModuleTypeRead] = Field(
        description="The analysis module type that was used to perform this analysis"
    )

    details: Optional[dict] = Field(description="A JSON representation of the details produced by the analysis")

    detection_points: List[NodeDetectionPointRead] = Field(
        description="A list of detection points added to the analysis"
    )

    uuid: UUID4 = Field(description="The UUID of the analysis")

    class Config:
        orm_mode = True


class AnalysisUpdate(NodeUpdate, AnalysisBase):
    details: Optional[Json] = Field(description="A JSON representation of the details produced by the analysis")

    error_message: Optional[type_str] = Field(description="An optional error message that occurred during analysis")

    stack_trace: Optional[type_str] = Field(description="An optional stack trace that occurred during analysis")
