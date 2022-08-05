import json

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, func, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing import Optional

from api_models.submission import SubmissionHistorySnapshot, SubmissionRead, SubmissionTreeRead
from db.database import Base
from db.schemas.analysis import Analysis
from db.schemas.analysis_mode import AnalysisMode
from db.schemas.analysis_status import AnalysisStatus
from db.schemas.helpers import utcnow
from db.schemas.history import HasHistory, HistoryMixin
from db.schemas.metadata_detection_point import MetadataDetectionPoint
from db.schemas.metadata_tag import MetadataTag
from db.schemas.observable import Observable
from db.schemas.submission_analysis_mapping import submission_analysis_mapping
from db.schemas.submission_tag_mapping import submission_tag_mapping


class SubmissionHistory(Base, HistoryMixin):
    __tablename__ = "submission_history"

    record_uuid = Column(UUID(as_uuid=True), ForeignKey("submission.uuid"), index=True, nullable=False)


class Submission(Base, HasHistory):
    __tablename__ = "submission"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    alert = Column(Boolean, default=False, nullable=False, index=True)

    analyses: list[Analysis] = relationship("Analysis", secondary=submission_analysis_mapping)

    # This relationship is used to get a list of the unique analysis statuses within the submission. It is then
    # used to determine the "overall" status for the submission. For example, if any of the statuses in this list
    # is "running", then the submission's status will be "running". If there is only a single status in this list,
    # then that will be the submission's status.
    analysis_statuses: list[AnalysisStatus] = relationship(
        "AnalysisStatus",
        secondary="join(AnalysisStatus, Analysis, AnalysisStatus.uuid == Analysis.status_uuid)."
        "join(submission_analysis_mapping, submission_analysis_mapping.c.analysis_uuid == Analysis.uuid)",
        primaryjoin="Submission.uuid == submission_analysis_mapping.c.submission_uuid",
        uselist=True,
        viewonly=True,
    )

    # This association proxy is used for associating analysis metadata with observables
    analysis_uuids: list[UUID] = association_proxy("analyses", "uuid")

    # The child_* fields use a composite join relationship to get a list of the objects that
    # are applied to any observables that exist in this submission's tree structure. For example, this is
    # used on the Manage Alerts page so that we can display ALL of the tags for a submission and
    # its children.
    #
    # While there is nothing too complicated about this SQL query, SQLAlchemy does not have a
    # straightforward way to handle these types of relationships with intermediate tables.
    # To solve this, you have to use the composite join relationship, which is described here:
    # https://docs.sqlalchemy.org/en/14/orm/join_conditions.html#composite-secondary-joins
    #
    # The overall goal is that you use the "secondary" parameter in the relationship to construct
    # the intermediate table that you need. You then use the "primaryjoin" and, if needed, the
    # "secondaryjoin" parameters to tell SQLAlchemy how to join the child object against the
    # parent object (where in this case Submission is the parent, and the child object is the child).
    #
    # Finally, "viewonly" is used on the relationship to prevent attempts to add tags to this list.

    child_analysis_tags: list[MetadataTag] = relationship(
        "MetadataTag",
        secondary="join(AnalysisMetadata, MetadataTag, MetadataTag.uuid == AnalysisMetadata.metadata_uuid)."
        "join(submission_analysis_mapping, submission_analysis_mapping.c.analysis_uuid == AnalysisMetadata.analysis_uuid)",
        primaryjoin="Submission.uuid == submission_analysis_mapping.c.submission_uuid",
        # NOTE: The secondaryjoin parameter is required specifically when using the
        # crud.submission.read_all() function to filter submissions by their tags.
        # Without it, the query that SQLAlchemy creates results in the returned submissions
        # having every tag from every submission in their child_analysis_tags list.
        secondaryjoin="Metadata.uuid == AnalysisMetadata.metadata_uuid",
        order_by="asc(MetadataTag.value)",
        viewonly=True,
    )

    child_detection_points: list[MetadataDetectionPoint] = relationship(
        "MetadataDetectionPoint",
        secondary="join(AnalysisMetadata, MetadataDetectionPoint, MetadataDetectionPoint.uuid == AnalysisMetadata.metadata_uuid)."
        "join(submission_analysis_mapping, submission_analysis_mapping.c.analysis_uuid == AnalysisMetadata.analysis_uuid)",
        primaryjoin="Submission.uuid == submission_analysis_mapping.c.submission_uuid",
        secondaryjoin="Metadata.uuid == AnalysisMetadata.metadata_uuid",
        order_by="asc(MetadataDetectionPoint.value)",
        viewonly=True,
    )

    child_observables: list[Observable] = relationship(
        "Observable",
        secondary="join(Observable, analysis_child_observable_mapping, Observable.uuid == analysis_child_observable_mapping.c.observable_uuid)."
        "join(submission_analysis_mapping, submission_analysis_mapping.c.analysis_uuid == analysis_child_observable_mapping.c.analysis_uuid)",
        primaryjoin="Submission.uuid == submission_analysis_mapping.c.submission_uuid",
        viewonly=True,
    )

    child_tags: list[MetadataTag] = relationship(
        "MetadataTag",
        secondary="join(MetadataTag, observable_tag_mapping, MetadataTag.uuid == observable_tag_mapping.c.tag_uuid)."
        "join(analysis_child_observable_mapping, analysis_child_observable_mapping.c.observable_uuid == observable_tag_mapping.c.observable_uuid)."
        "join(submission_analysis_mapping, submission_analysis_mapping.c.analysis_uuid == analysis_child_observable_mapping.c.analysis_uuid)",
        primaryjoin="Submission.uuid == submission_analysis_mapping.c.submission_uuid",
        secondaryjoin="MetadataTag.uuid == observable_tag_mapping.c.tag_uuid",
        foreign_keys="[Submission.uuid, MetadataTag.uuid]",
        order_by="asc(MetadataTag.value)",
        viewonly=True,
    )

    comments = relationship("SubmissionComment", viewonly=True)

    # The analysis mode to use if the submission turns into an alert
    analysis_mode_alert_uuid = Column(UUID(as_uuid=True), ForeignKey("analysis_mode.uuid"), nullable=False, index=True)

    analysis_mode_alert: AnalysisMode = relationship("AnalysisMode", foreign_keys=[analysis_mode_alert_uuid])

    # The submission's current analysis mode
    analysis_mode_current_uuid = Column(
        UUID(as_uuid=True), ForeignKey("analysis_mode.uuid"), nullable=False, index=True
    )

    analysis_mode_current: AnalysisMode = relationship("AnalysisMode", foreign_keys=[analysis_mode_current_uuid])

    # The analysis mode to initially use when determining if the submission should be an alert
    analysis_mode_detect_uuid = Column(UUID(as_uuid=True), ForeignKey("analysis_mode.uuid"), nullable=False, index=True)

    analysis_mode_detect: AnalysisMode = relationship("AnalysisMode", foreign_keys=[analysis_mode_detect_uuid])

    # The analysis mode to use if the submission is added to an event
    analysis_mode_event_uuid = Column(UUID(as_uuid=True), ForeignKey("analysis_mode.uuid"), nullable=False, index=True)

    analysis_mode_event: AnalysisMode = relationship("AnalysisMode", foreign_keys=[analysis_mode_event_uuid])

    # The submission mode to use if response tasks are needed for the submission
    analysis_mode_response_uuid = Column(
        UUID(as_uuid=True), ForeignKey("analysis_mode.uuid"), nullable=False, index=True
    )

    analysis_mode_response: AnalysisMode = relationship("AnalysisMode", foreign_keys=[analysis_mode_response_uuid])

    description = Column(String)

    disposition = relationship("AlertDisposition")

    disposition_uuid = Column(UUID(as_uuid=True), ForeignKey("alert_disposition.uuid"), index=True)

    # Stores the most recent time the submission was dispositioned.
    # Needed for the "sort by disposition_time" feature.
    disposition_time = Column(DateTime(timezone=True), index=True)

    # Stores the user UUID of who most recently dispositioned the submission.
    # Needed for the "sort by disposition_user" feature.
    disposition_user_uuid = Column(UUID(as_uuid=True), ForeignKey("user.uuid"), index=True)

    disposition_user = relationship("User", foreign_keys=[disposition_user_uuid])

    event_time = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False, index=True)

    event_uuid = Column(UUID(as_uuid=True), ForeignKey("event.uuid"), index=True)

    event = relationship("Event", foreign_keys=[event_uuid])

    history = relationship(
        "SubmissionHistory",
        primaryjoin="SubmissionHistory.record_uuid == Submission.uuid",
        order_by="SubmissionHistory.action_time",
    )

    insert_time = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False, index=True)

    instructions = Column(String)

    # This gets populated by certain submission-related queries.
    matching_events = None

    name = Column(String, nullable=False)

    # This gets populated by certain submission-related queries.
    number_of_observables = 0

    owner_uuid = Column(UUID(as_uuid=True), ForeignKey("user.uuid"), index=True)

    owner = relationship("User", foreign_keys=[owner_uuid])

    # Stores the most recent time the submission changed owners
    ownership_time = Column(DateTime(timezone=True), index=True)

    queue = relationship("Queue")

    queue_uuid = Column(UUID(as_uuid=True), ForeignKey("queue.uuid"), nullable=False, index=True)

    root_analysis_uuid = Column(UUID(as_uuid=True), ForeignKey("analysis.uuid"), nullable=False, index=True)

    root_analysis: Analysis = relationship("Analysis", foreign_keys=[root_analysis_uuid])

    tags: list[MetadataTag] = relationship("MetadataTag", secondary=submission_tag_mapping)

    tool = relationship("SubmissionTool")

    tool_uuid = Column(UUID(as_uuid=True), ForeignKey("submission_tool.uuid"), index=True)

    tool_instance = relationship("SubmissionToolInstance")

    tool_instance_uuid = Column(UUID(as_uuid=True), ForeignKey("submission_tool_instance.uuid"), index=True)

    type = relationship("SubmissionType")

    type_uuid = Column(UUID(as_uuid=True), ForeignKey("submission_type.uuid"), nullable=False, index=True)

    version = Column(UUID(as_uuid=True), server_default=func.gen_random_uuid(), nullable=False)

    __table_args__ = (
        Index(
            "name_trgm",
            name,
            postgresql_ops={"name": "gin_trgm_ops"},
            postgresql_using="gin",
        ),
    )

    def convert_to_pydantic(self, root_analysis) -> SubmissionTreeRead:
        return SubmissionTreeRead(root_analysis=root_analysis, **self.to_dict())

    def to_dict(self):
        ignore_keys = [
            "analyses",
            "analysis_statuses",
            "analysis_uuids",
            "child_observables",
            "event",
            "history",
            "history_snapshot",
            "root_analysis",
            "to_dict",
        ]

        return {key: getattr(self, key) for key in self.__class__.__dict__ if key not in ignore_keys}

    @property
    def history_snapshot(self):
        return json.loads(SubmissionHistorySnapshot(**self.to_dict()).json())

    @property
    def disposition_time_earliest(self) -> Optional[datetime]:
        """Returns the earliest time the submission was dispositioned"""
        history: Optional[SubmissionHistory] = next((x for x in self.history if x.field == "disposition"), None)
        if history:
            return history.action_time
        return None

    @property
    def ownership_time_earliest(self) -> Optional[datetime]:
        """Returns the earliest time an analyst took ownership of the submission"""
        history: Optional[SubmissionHistory] = next((x for x in self.history if x.field == "owner"), None)
        if history:
            return history.action_time
        return None

    @property
    def status(self) -> AnalysisStatus:
        """Determines the submission's overall analysis status"""

        # Possible status combinations are:
        #
        # running -> running
        # ignore -> ignore
        # complete -> complete
        # complete, running -> running
        # complete, ignore -> complete
        # ignore, running -> running
        # complete, running, ignore -> running

        # If there is only a single status, then use that one
        if len(self.analysis_statuses) == 1:
            return self.analysis_statuses[0]

        # If any of the statuses is "running" then use that
        running = next((s for s in self.analysis_statuses if s.value == "running"), None)
        if running is not None:
            return running

        # Otherwise at this point the statuses must be "complete" and "ignore", so use "complete"
        return next(s for s in self.analysis_statuses if s.value == "complete")


from api_models.analysis import RootAnalysisSubmissionTreeRead

RootAnalysisSubmissionTreeRead.update_forward_refs()
