from sqlalchemy import func, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from schemas.threat_actor_queue_mapping import threat_actor_queue_mapping


class ThreatActor(Base):
    __tablename__ = "threat_actor"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    description = Column(String)

    queues = relationship("Queue", secondary=threat_actor_queue_mapping)

    value = Column(String, nullable=False, unique=True, index=True)
