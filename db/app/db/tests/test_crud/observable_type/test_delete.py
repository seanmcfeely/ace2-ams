from db import crud
from db.tests import factory


def test_delete(db):
    obj = factory.observable_type.create_or_read(value="test", db=db)
    assert crud.observable_type.delete(uuid=obj.uuid, db=db) is True


def test_unable_to_delete(db):
    obj = factory.observable_type.create_or_read(value="test", db=db)

    submission = factory.submission.create(db=db)
    factory.observable.create_or_read(type="test", value="value", parent_analysis=submission.root_analysis, db=db)

    # You should not be able to delete it now that it is in use
    assert crud.observable_type.delete(uuid=obj.uuid, db=db) is False
