from sqlalchemy.orm import Session

import crud
from api_models.analysis_mode import AnalysisModeCreate


def create_or_read(value: str, db: Session, analysis_module_types: list[str] = None):
    if analysis_module_types is None:
        analysis_module_types = []

    return crud.analysis_mode.create_or_read(
        model=AnalysisModeCreate(analysis_module_types=analysis_module_types, value=value), db=db
    )
