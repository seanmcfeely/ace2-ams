from sqlalchemy.orm import Session

from db import crud
from api_models.submission_tool_instance import SubmissionToolInstanceCreate


def create_or_read(value: str, db: Session):
    return crud.submission_tool_instance.create_or_read(model=SubmissionToolInstanceCreate(value=value), db=db)
