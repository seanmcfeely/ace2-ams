from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from database import Base


analysis_mode_analysis_module_type_mapping = Table(
    "analysis_mode_analysis_module_type_mapping",
    Base.metadata,
    Column(
        "analysis_mode_uuid",
        UUID(as_uuid=True),
        ForeignKey("analysis_mode.uuid", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    ),
    Column(
        "analysis_module_type_uuid",
        UUID(as_uuid=True),
        ForeignKey("analysis_module_type.uuid"),
        index=True,
        primary_key=True,
    ),
)
