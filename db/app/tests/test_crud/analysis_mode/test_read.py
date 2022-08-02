import crud
from tests import factory


def test_read_all(db):
    # conftest automatically creates four analysis mode objects since they are required for creating submissions
    result = crud.analysis_mode.read_all(db=db)
    assert len(result) == 4
    assert any(s.value == "default_alert" for s in result)
    assert any(s.value == "default_detect" for s in result)
    assert any(s.value == "default_event" for s in result)
    assert any(s.value == "default_response" for s in result)


def test_read_by_uuid(db):
    obj = factory.analysis_mode.create_or_read(value="test", db=db)

    result = crud.analysis_mode.read_by_uuid(uuid=obj.uuid, db=db)
    assert result.uuid == obj.uuid


def test_read_by_value(db):
    obj = factory.analysis_mode.create_or_read(value="test", db=db)

    result = crud.analysis_mode.read_by_value(value=obj.value, db=db)
    assert result.uuid == obj.uuid
