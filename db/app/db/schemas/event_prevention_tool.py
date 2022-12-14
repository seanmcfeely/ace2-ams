from sqlalchemy import func, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.database import Base
from db.schemas.event_prevention_tool_queue_mapping import event_prevention_tool_queue_mapping


class EventPreventionTool(Base):
    __tablename__ = "event_prevention_tool"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    description = Column(String)

    queues = relationship("Queue", secondary=event_prevention_tool_queue_mapping)

    value = Column(String, nullable=False, unique=True, index=True)
