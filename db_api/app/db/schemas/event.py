import json

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, func, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing import Optional

from api_models.alert_disposition import AlertDispositionRead
from api_models.event import EventRead
from db.database import Base
from db.schemas.analysis_module_type import AnalysisModuleType
from db.schemas.event_prevention_tool_mapping import event_prevention_tool_mapping
from db.schemas.event_remediation_mapping import event_remediation_mapping
from db.schemas.event_tag_mapping import event_tag_mapping
from db.schemas.event_threat_actor_mapping import event_threat_actor_mapping
from db.schemas.event_threat_mapping import event_threat_mapping
from db.schemas.event_vector_mapping import event_vector_mapping
from db.schemas.helpers import utcnow
from db.schemas.history import HasHistory, HistoryMixin
from db.schemas.metadata_tag import MetadataTag
from db.schemas.submission import Submission


class EventHistory(Base, HistoryMixin):
    __tablename__ = "event_history"

    record_uuid = Column(UUID(as_uuid=True), ForeignKey("event.uuid"), index=True, nullable=False)


class Event(Base, HasHistory):
    __tablename__ = "event"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    alert_time = Column(DateTime(timezone=True), index=True)

    alerts: list[Submission] = relationship(
        "Submission", primaryjoin="Submission.event_uuid == Event.uuid", viewonly=True
    )

    alert_uuids = association_proxy("alerts", "uuid")

    analysis_module_types: list[AnalysisModuleType] = relationship(
        "AnalysisModuleType",
        secondary="join(AnalysisModuleType, Analysis, AnalysisModuleType.uuid == Analysis.analysis_module_type_uuid)."
        "join(submission_analysis_mapping, submission_analysis_mapping.c.analysis_uuid == Analysis.uuid)."
        "join(Submission, Submission.uuid == submission_analysis_mapping.c.submission_uuid)",
        primaryjoin="Event.uuid == Submission.event_uuid",
        order_by="asc(AnalysisModuleType.value)",
        uselist=True,
        viewonly=True,
    )

    analysis_types: list[str] = association_proxy("analysis_module_types", "value")

    comments = relationship("EventComment", viewonly=True)

    # There isn't currently a way to automatically calculate this time
    contain_time = Column(DateTime(timezone=True), index=True)

    created_time = Column(DateTime(timezone=True), server_default=utcnow(), index=True)

    disposition_time = Column(DateTime(timezone=True), index=True)

    event_time = Column(DateTime(timezone=True), index=True)

    history: list[EventHistory] = relationship(
        "EventHistory",
        primaryjoin="EventHistory.record_uuid == Event.uuid",
        order_by="EventHistory.action_time",
    )

    name = Column(String, nullable=False)

    owner_uuid = Column(UUID(as_uuid=True), ForeignKey("user.uuid"), nullable=True)

    owner = relationship("User", foreign_keys=[owner_uuid])

    ownership_time = Column(DateTime(timezone=True), index=True)

    prevention_tools = relationship("EventPreventionTool", secondary=event_prevention_tool_mapping)

    queue = relationship("Queue")

    queue_uuid = Column(UUID(as_uuid=True), ForeignKey("queue.uuid"), nullable=False, index=True)

    # There isn't currently a way to automatically calculate this time
    remediation_time = Column(DateTime(timezone=True), index=True)

    remediations = relationship("EventRemediation", secondary=event_remediation_mapping)

    severity = relationship("EventSeverity")

    severity_uuid = Column(UUID(as_uuid=True), ForeignKey("event_severity.uuid"))

    source = relationship("EventSource")

    source_uuid = Column(UUID(as_uuid=True), ForeignKey("event_source.uuid"))

    status = relationship("EventStatus")

    status_uuid = Column(UUID(as_uuid=True), ForeignKey("event_status.uuid"), nullable=False)

    tags: list[MetadataTag] = relationship("MetadataTag", secondary=event_tag_mapping)

    threat_actors = relationship("ThreatActor", secondary=event_threat_actor_mapping)

    threats = relationship("Threat", secondary=event_threat_mapping)

    type = relationship("EventType")

    type_uuid = Column(UUID(as_uuid=True), ForeignKey("event_type.uuid"))

    vectors = relationship("EventVector", secondary=event_vector_mapping)

    version = Column(UUID(as_uuid=True), server_default=func.gen_random_uuid(), nullable=False)

    def convert_to_pydantic(self) -> EventRead:
        return EventRead(**self.to_dict())

    def to_dict(self):
        return {
            "alert_time": self.alert_time,
            "alert_uuids": self.alert_uuids,
            "all_tags": self.all_tags,
            "analysis_types": self.analysis_types,
            "auto_alert_time": self.auto_alert_time,
            "auto_disposition_time": self.auto_disposition_time,
            "auto_event_time": self.auto_event_time,
            "auto_ownership_time": self.auto_ownership_time,
            "comments": self.comments,
            "contain_time": self.contain_time,
            "created_time": self.created_time,
            "disposition": self.disposition,
            "disposition_time": self.disposition_time,
            "event_time": self.event_time,
            "name": self.name,
            "owner": self.owner,
            "ownership_time": self.ownership_time,
            "prevention_tools": self.prevention_tools,
            "queue": self.queue,
            "remediation_time": self.remediation_time,
            "remediations": self.remediations,
            "severity": self.severity,
            "source": self.source,
            "status": self.status,
            "tags": self.tags,
            "threat_actors": self.threat_actors,
            "threats": self.threats,
            "type": self.type,
            "uuid": self.uuid,
            "vectors": self.vectors,
            "version": self.version,
        }

    @property
    def history_snapshot(self):
        return json.loads(self.convert_to_pydantic().json())

    @property
    def all_tags(self) -> list[MetadataTag]:
        """Returns a list of every tag contained within the event sorted by their values"""

        # Start by creating a copy of the event's tags so that we are not using the same reference.
        results = list(self.tags)
        for alert in self.alerts:
            results += alert.tags
            results += alert.child_analysis_tags
            results += alert.child_tags

        return sorted(set(results), key=lambda x: x.value)

    @property
    def auto_alert_time(self) -> Optional[datetime]:
        """Returns the earliest time an alert in the event was created"""
        if self.alerts:
            return sorted(self.alerts, key=lambda x: x.insert_time)[0].insert_time
        return None

    @property
    def auto_disposition_time(self) -> Optional[datetime]:
        """Returns the earliest time an alert in the event was dispositioned"""
        if self.alerts:
            return sorted(
                self.alerts, key=lambda x: (x.disposition_time_earliest is None, x.disposition_time_earliest)
            )[0].disposition_time_earliest
        return None

    @property
    def auto_event_time(self) -> Optional[datetime]:
        """Returns the earliest event time from the alerts in the event"""
        if self.alerts:
            return sorted(self.alerts, key=lambda x: x.event_time)[0].event_time
        return None

    @property
    def auto_ownership_time(self) -> Optional[datetime]:
        """Returns the earliest time an analyst took ownership of an alert in the event"""
        if self.alerts:
            return sorted(self.alerts, key=lambda x: (x.ownership_time_earliest is None, x.ownership_time_earliest))[
                0
            ].ownership_time_earliest
        return None

    @property
    def disposition(self) -> Optional[AlertDispositionRead]:
        """Returns the highest disposition used on the alerts in the event"""
        if alerts_with_disposition := [a for a in self.alerts if a.disposition]:
            return sorted(alerts_with_disposition, key=lambda x: x.disposition.rank)[-1].disposition
        return None
