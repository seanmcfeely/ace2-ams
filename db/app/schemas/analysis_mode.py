from sqlalchemy import func, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from schemas.analysis_mode_analysis_module_type_mapping import analysis_mode_analysis_module_type_mapping
from schemas.analysis_module_type import AnalysisModuleType


class AnalysisMode(Base):
    __tablename__ = "analysis_mode"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    analysis_module_types: list[AnalysisModuleType] = relationship(
        "AnalysisModuleType", secondary=analysis_mode_analysis_module_type_mapping, uselist=True
    )

    description = Column(String)

    value = Column(String, nullable=False, unique=True, index=True)
