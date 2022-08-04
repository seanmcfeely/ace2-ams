from db import crud
from db.tests import factory


def test_delete(db):
    obj = factory.analysis_mode.create_or_read(value="test", db=db)
    assert crud.analysis_mode.delete(uuid=obj.uuid, db=db) is True


def test_unable_to_delete(db):
    obj = factory.analysis_mode.create_or_read(value="test", db=db)
    factory.submission.create(analysis_mode_alert="test", db=db)

    # You should not be able to delete it now that it is in use
    assert crud.analysis_mode.delete(uuid=obj.uuid, db=db) is False
