import pytest

from uuid import uuid4

from db import crud
from db.exceptions import UuidNotFoundInDatabase
from db.tests import factory


#
# INVALID TESTS
#


def test_delete_nonexistent(db):
    with pytest.raises(UuidNotFoundInDatabase):
        crud.alert_disposition.delete(uuid=uuid4(), db=db)


def test_unable_to_delete(db):
    obj = factory.alert_disposition.create_or_read(value="test", rank=1, db=db)
    factory.submission.create(alert=True, disposition="test", db=db)

    # You should not be able to delete it now that it is in use
    assert crud.alert_disposition.delete(uuid=obj.uuid, db=db) is False


#
# VALID TESTS
#


def test_delete(db):
    obj = factory.alert_disposition.create_or_read(value="test", rank=1, db=db)
    assert crud.alert_disposition.delete(uuid=obj.uuid, db=db) is True
