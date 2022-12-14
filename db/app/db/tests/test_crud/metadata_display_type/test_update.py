from api_models.metadata_display_type import MetadataDisplayTypeUpdate
from db import crud
from db.tests import factory


def test_update(db):
    obj = factory.metadata_display_type.create_or_read(value="test", db=db)

    assert obj.description is None
    assert obj.value == "test"

    crud.metadata_display_type.update(
        uuid=obj.uuid,
        model=MetadataDisplayTypeUpdate(description="test description", value="new value"),
        db=db,
    )

    assert obj.description == "test description"
    assert obj.value == "new value"


def test_update_duplicate_value(db):
    obj1 = factory.metadata_display_type.create_or_read(value="test", db=db)
    obj2 = factory.metadata_display_type.create_or_read(value="test2", db=db)

    result = crud.metadata_display_type.update(uuid=obj2.uuid, model=MetadataDisplayTypeUpdate(value=obj1.value), db=db)
    assert result is False
