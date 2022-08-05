from sqlalchemy.orm import Session

from db import crud
from api_models.analysis_status import AnalysisStatusCreate


def create_or_read(value: str, db: Session):
    return crud.analysis_status.create_or_read(model=AnalysisStatusCreate(value=value), db=db)
