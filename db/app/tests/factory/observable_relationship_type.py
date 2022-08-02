from sqlalchemy.orm import Session

import crud
from api_models.observable_relationship_type import ObservableRelationshipTypeCreate


def create_or_read(value: str, db: Session):
    return crud.observable_relationship_type.create_or_read(model=ObservableRelationshipTypeCreate(value=value), db=db)
