import json

from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

from db import crud
from api_models.analysis import AnalysisCreate
from api_models.observable import ObservableCreate
from db.schemas.analysis_module_type import AnalysisModuleType
from db.schemas.observable import Observable
from db.schemas.submission import Submission
from db.tests import factory


def create_or_read(
    analysis_module_type: AnalysisModuleType,
    submission: Submission,
    target: Observable,
    db: Session,
    child_observables: list[ObservableCreate] = None,
    details: Optional[dict] = None,
    error_message: str = None,
    run_time: Optional[datetime] = None,
    stack_trace: str = None,
    status: str = "running",
    summary: str = None,
):
    factory.analysis_status.create_or_read(value=status, db=db)

    if child_observables is None:
        child_observables = []

    if run_time is None:
        run_time = crud.helpers.utcnow()

    return crud.analysis.create_or_read(
        model=AnalysisCreate(
            analysis_module_type_uuid=analysis_module_type.uuid,
            child_observables=child_observables,
            details=json.dumps(details),
            error_message=error_message,
            run_time=run_time,
            stack_trace=stack_trace,
            status=status,
            submission_uuid=submission.uuid,
            summary=summary,
            target_uuid=target.uuid,
        ),
        db=db,
    )
