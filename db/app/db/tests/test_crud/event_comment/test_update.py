from api_models.event_comment import EventCommentUpdate
from db import crud
from db.tests import factory


def test_update(db):
    new_user = factory.user.create_or_read(username="new_user", db=db)
    event = factory.event.create_or_read(name="test", db=db)
    obj = factory.event_comment.create_or_read(event=event, username="analyst", value="test", db=db)

    assert obj.user.username == "analyst"
    assert obj.value == "test"

    crud.event_comment.update(
        uuid=obj.uuid,
        model=EventCommentUpdate(username="new_user", value="new value"),
        db=db,
    )

    assert obj.user == new_user
    assert obj.value == "new value"


def test_update_duplicate_event_and_value(db):
    event = factory.event.create_or_read(name="test", db=db)
    obj1 = factory.event_comment.create_or_read(event=event, username="analyst", value="test", db=db)
    obj2 = factory.event_comment.create_or_read(event=event, username="analyst", value="test2", db=db)

    result = crud.event_comment.update(
        uuid=obj2.uuid, model=EventCommentUpdate(username="analyst", value=obj1.value), db=db
    )
    assert result is False
