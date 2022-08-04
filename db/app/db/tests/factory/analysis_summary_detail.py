from sqlalchemy.orm import Session

from db import crud
from api_models.analysis_summary_detail import AnalysisSummaryDetailCreate
from db.schemas.analysis import Analysis
from db.tests import factory


def create_or_read(
    analysis: Analysis,
    header: str,
    content: str,
    db: Session,
    format: str = "PRE",
):
    factory.format.create_or_read(value=format, db=db)

    obj = crud.analysis_summary_detail.create_or_read(
        model=AnalysisSummaryDetailCreate(analysis_uuid=analysis.uuid, content=content, header=header, format=format),
        db=db,
    )

    db.commit()
    return obj
