from sqlalchemy.orm import Session

import crud
from api_models.submission_type import SubmissionTypeCreate


def create_or_read(value: str, db: Session):
    return crud.submission_type.create_or_read(model=SubmissionTypeCreate(value=value), db=db)
