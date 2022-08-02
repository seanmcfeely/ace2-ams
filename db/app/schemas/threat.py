from sqlalchemy import func, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from schemas.threat_threat_type_mapping import (
    threat_threat_type_mapping,
)
from schemas.threat_queue_mapping import threat_queue_mapping


class Threat(Base):
    __tablename__ = "threat"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    description = Column(String)

    queues = relationship("Queue", secondary=threat_queue_mapping)

    types = relationship("ThreatType", secondary=threat_threat_type_mapping, passive_deletes=True)

    value = Column(String, nullable=False, unique=True, index=True)
