from sqlalchemy import func, Column, String
from sqlalchemy.dialects.postgresql import UUID

from db.database import Base


class NodeDirective(Base):
    __tablename__ = "node_directive"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    description = Column(String)

    value = Column(String, nullable=False, unique=True, index=True)
