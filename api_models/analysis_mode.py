from pydantic import BaseModel, Field, UUID4
from typing import Optional
from uuid import uuid4

from api_models import type_list_str, type_str, validators
from api_models.analysis_module_type import AnalysisModuleTypeRead


class AnalysisModeBase(BaseModel):
    """Represents a mode that is applied to an analysis."""

    description: Optional[type_str] = Field(description="An optional human-readable description of the analysis mode")

    value: type_str = Field(description="The value of the analysis mode")


class AnalysisModeCreate(AnalysisModeBase):
    analysis_module_types: list[str] = Field(
        default_factory=list, description="The list of analysis module types included in this mode"
    )

    uuid: UUID4 = Field(default_factory=uuid4, description="The UUID of the analysis mode")


class AnalysisModeRead(AnalysisModeBase):
    analysis_module_types: list[AnalysisModuleTypeRead] = Field(
        description="The list of analysis module types included in this mode"
    )

    uuid: UUID4 = Field(description="The UUID of the analysis mode")

    class Config:
        orm_mode = True


class AnalysisModeUpdate(AnalysisModeBase):
    analysis_module_types: Optional[type_list_str] = Field(
        description="The list of analysis module types included in this mode"
    )

    value: Optional[type_str] = Field(description="The value of the analysis mode")

    _prevent_none: classmethod = validators.prevent_none("analysis_module_types", "value")
