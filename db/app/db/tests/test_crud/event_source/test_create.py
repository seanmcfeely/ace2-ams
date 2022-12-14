from api_models.event_source import EventSourceCreate
from db import crud
from db.tests import factory


def test_create(db):
    queue = factory.queue.create_or_read(value="test_queue", db=db)

    obj = crud.event_source.create_or_read(
        model=EventSourceCreate(description="test description", value="test", queues=["test_queue"]),
        db=db,
    )

    assert obj.description == "test description"
    assert obj.queues == [queue]
    assert obj.value == "test"


def test_create_duplicate(db):
    obj = crud.event_source.create_or_read(model=EventSourceCreate(value="test", queues=["external"]), db=db)
    obj2 = crud.event_source.create_or_read(model=EventSourceCreate(value="test", queues=["external"]), db=db)

    assert obj2.uuid == obj.uuid
