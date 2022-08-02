from sqlalchemy import func, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from schemas.event_status_queue_mapping import event_status_queue_mapping


class EventStatus(Base):
    __tablename__ = "event_status"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    description = Column(String)

    queues = relationship("Queue", secondary=event_status_queue_mapping)

    value = Column(String, nullable=False, unique=True, index=True)
