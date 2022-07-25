from sqlalchemy.orm import Session

from api_models.analysis_mode import AnalysisModeCreate
from db import crud


def create_or_read(value: str, db: Session):
    return crud.analysis_mode.create_or_read(model=AnalysisModeCreate(value=value), db=db)
