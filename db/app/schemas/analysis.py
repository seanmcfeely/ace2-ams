from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, func, Index, String
from sqlalchemy.dialects.postgresql import ExcludeConstraint, JSONB, TSTZRANGE, UUID
from sqlalchemy.orm import deferred, relationship
from typing import Optional

from api_models.analysis import AnalysisSubmissionTreeRead
from database import Base
from schemas.analysis_child_observable_mapping import analysis_child_observable_mapping
from schemas.helpers import utcnow
from schemas.observable import Observable


class Analysis(Base):
    __tablename__ = "analysis"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    analysis_module_type = relationship("AnalysisModuleType")

    # An analysis with NULL for analysis_module_type_uuid and target_uuid signifies it is a Root Analysis
    analysis_module_type_uuid = Column(UUID(as_uuid=True), ForeignKey("analysis_module_type.uuid"), nullable=True)

    cached_during = Column(TSTZRANGE(), nullable=True)

    child_observables: list[Observable] = relationship("Observable", secondary=analysis_child_observable_mapping)

    # Using deferred means that when you query the Analysis table, you will not select the details field unless
    # you explicitly ask for it. This is so that we can more efficiently load alert trees without selecting
    # all of the analysis details, which can be very large.
    details = deferred(Column(JSONB))

    error_message = Column(String)

    run_time = Column(DateTime(timezone=True), server_default=utcnow(), index=True, nullable=False)

    stack_trace = Column(String)

    # NOTE: It is assumed that the analysis status values are "hard coded" to be: running, complete, and ignore.
    # If these are changed or more added, then you will also need to update the Submission.status @property so
    # that it can correctly determine the submission's overall status.
    status = relationship("AnalysisStatus")

    status_uuid = Column(UUID(as_uuid=True), ForeignKey("analysis_status.uuid"), nullable=False)

    summary = Column(String)

    summary_details: "list[AnalysisSummaryDetail]" = relationship("AnalysisSummaryDetail")

    # An analysis with NULL for analysis_module_type_uuid and target_uuid signifies it is a Root Analysis
    target_uuid = Column(UUID(as_uuid=True), ForeignKey("observable.uuid"), nullable=True)

    target: Observable = relationship("Observable", foreign_keys=[target_uuid])

    __table_args__ = (
        Index(
            "analysis_module_type_target_cached_during_idx",
            analysis_module_type_uuid,
            target_uuid,
            cached_during,
        ),
        # The PostgreSQL && operator is described here:
        # https://www.postgresql.org/docs/14/functions-array.html
        #
        # It just means that the two ranges overlap.
        ExcludeConstraint(
            ("analysis_module_type_uuid", "="),
            ("target_uuid", "="),
            ("cached_during", "&&"),
            name="cached_analysis_uc",
            using="gist",
        ),
    )

    @property
    def cached_until(self) -> Optional[datetime]:
        return self.cached_during.upper if self.cached_during else None

    def convert_to_pydantic(self) -> AnalysisSubmissionTreeRead:
        return AnalysisSubmissionTreeRead(leaf_id=f"{self.uuid}", **self.to_dict())

    def to_dict(self):
        ignore_keys = ["convert_to_pydantic", "to_dict"]
        return {key: getattr(self, key) for key in self.__class__.__dict__ if key not in ignore_keys}


from schemas.analysis_summary_detail import AnalysisSummaryDetail
