from db import crud
from tests import factory


def test_delete(db):
    obj = factory.observable_relationship_type.create_or_read(value="test", db=db)
    assert crud.observable_relationship_type.delete(uuid=obj.uuid, db=db) is True


def test_unable_to_delete(db):
    obj = factory.observable_relationship_type.create_or_read(value="test", db=db)

    submission = factory.submission.create(db=db)
    observable1 = factory.observable.create_or_read(
        type="type", value="value", parent_analysis=submission.root_analysis, db=db
    )
    observable2 = factory.observable.create_or_read(
        type="type", value="value2", parent_analysis=submission.root_analysis, db=db
    )
    factory.observable_relationship.create_or_read(
        observable=observable1, related_observable=observable2, type="test", db=db
    )

    # You should not be able to delete it now that it is in use
    assert crud.observable_relationship_type.delete(uuid=obj.uuid, db=db) is False
