from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from database import Base


threat_type_queue_mapping = Table(
    "threat_type_queue_mapping",
    Base.metadata,
    Column(
        "threat_type_uuid",
        UUID(as_uuid=True),
        ForeignKey("threat_type.uuid", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    ),
    Column(
        "queue_uuid",
        UUID(as_uuid=True),
        ForeignKey("queue.uuid"),
        index=True,
        primary_key=True,
    ),
)
