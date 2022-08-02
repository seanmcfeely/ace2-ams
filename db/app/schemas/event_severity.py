from sqlalchemy import func, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from schemas.event_severity_queue_mapping import event_severity_queue_mapping


class EventSeverity(Base):
    __tablename__ = "event_severity"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    description = Column(String)

    queues = relationship("Queue", secondary=event_severity_queue_mapping)

    value = Column(String, nullable=False, unique=True, index=True)
