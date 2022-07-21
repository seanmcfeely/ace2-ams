from api_models.metadata_tag import MetadataTagCreate
from db import crud


def test_create(db):
    obj = crud.metadata_tag.create_or_read(model=MetadataTagCreate(value="test value"), db=db)

    assert obj.description is None
    assert obj.value == "test value"


def test_create_duplicate_value(db):
    obj1 = crud.metadata_tag.create_or_read(model=MetadataTagCreate(value="test"), db=db)
    assert obj1

    # Ensure that you get the same object back if you try to create a duplicate value
    obj2 = crud.metadata_tag.create_or_read(model=MetadataTagCreate(value=obj1.value), db=db)
    assert obj2.description == obj1.description
    assert obj2.uuid == obj1.uuid
    assert obj2.value == obj1.value
