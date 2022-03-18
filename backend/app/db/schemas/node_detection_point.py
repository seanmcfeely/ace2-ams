from sqlalchemy import func, Column, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.database import Base
from db.schemas.helpers import utcnow


class NodeDetectionPoint(Base):
    __tablename__ = "node_detection_point"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    insert_time = Column(DateTime, server_default=utcnow())

    node_uuid = Column(UUID(as_uuid=True), ForeignKey("node.uuid"), index=True)

    node = relationship("Node", foreign_keys=[node_uuid], lazy="selectin")

    value = Column(String, nullable=False)

    __table_args__ = (
        Index(
            "value_trgm",
            value,
            postgresql_ops={"value": "gin_trgm_ops"},
            postgresql_using="gin",
        ),
        UniqueConstraint("node_uuid", "value", name="node_detection_point_value_uc"),
    )
