from api_models.analysis_mode import AnalysisModeUpdate
from db import crud
from tests import factory


def test_update(db):
    obj = factory.analysis_mode.create_or_read(value="test", db=db)

    assert obj.description is None
    assert obj.value == "test"

    crud.analysis_mode.update(
        uuid=obj.uuid,
        model=AnalysisModeUpdate(description="test description", value="new value"),
        db=db,
    )

    assert obj.description == "test description"
    assert obj.value == "new value"


def test_update_duplicate_value(db):
    obj1 = factory.analysis_mode.create_or_read(value="test", db=db)
    obj2 = factory.analysis_mode.create_or_read(value="test2", db=db)

    result = crud.analysis_mode.update(uuid=obj2.uuid, model=AnalysisModeUpdate(value=obj1.value), db=db)
    assert result is False
