from sqlalchemy.orm import Session

from db import crud
from api_models.user_role import UserRoleCreate


def create_or_read(value: str, db: Session):
    return crud.user_role.create_or_read(model=UserRoleCreate(value=value), db=db)
