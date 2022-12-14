from api_models.metadata_detection_point import MetadataDetectionPointUpdate
from db import crud
from db.tests import factory


def test_update(db):
    obj = factory.metadata_detection_point.create_or_read(value="test", db=db)

    assert obj.description is None
    assert obj.value == "test"

    crud.metadata_detection_point.update(
        uuid=obj.uuid,
        model=MetadataDetectionPointUpdate(description="test description", value="new value"),
        db=db,
    )

    assert obj.description == "test description"
    assert obj.value == "new value"


def test_update_duplicate_value(db):
    obj1 = factory.metadata_detection_point.create_or_read(value="test", db=db)
    obj2 = factory.metadata_detection_point.create_or_read(value="test2", db=db)

    result = crud.metadata_detection_point.update(
        uuid=obj2.uuid, model=MetadataDetectionPointUpdate(value=obj1.value), db=db
    )
    assert result is False
