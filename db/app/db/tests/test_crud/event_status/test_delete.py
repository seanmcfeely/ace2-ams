from db import crud
from db.tests import factory


def test_delete(db):
    obj = factory.event_status.create_or_read(value="test", db=db)
    assert crud.event_status.delete(uuid=obj.uuid, db=db) is True


def test_unable_to_delete(db):
    obj = factory.event_status.create_or_read(value="test", db=db)
    factory.event.create_or_read(name="test", status="test", db=db)

    # You should not be able to delete it now that it is in use
    assert crud.event_status.delete(uuid=obj.uuid, db=db) is False
