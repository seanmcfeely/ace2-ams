import pytest
import uuid

from fastapi import status

from tests import helpers


#
# INVALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("description", 123),
        ("description", ""),
        ("queues", None),
        ("queues", "test_queue"),
        ("queues", [123]),
        ("queues", [None]),
        ("queues", [""]),
        ("queues", ["abc", 123]),
        ("value", 123),
        ("value", None),
        ("value", ""),
    ],
)
def test_update_invalid_fields(client, key, value):
    update = client.patch(f"/api/event/risk_level/{uuid.uuid4()}", json={key: value})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_invalid_uuid(client):
    update = client.patch("/api/event/risk_level/1", json={"value": "test"})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "key",
    [
        ("value"),
    ],
)
def test_update_duplicate_unique_fields(client, db, key):
    # Create some objects
    obj1 = helpers.create_event_risk_level(value="test", db=db)
    obj2 = helpers.create_event_risk_level(value="test2", db=db)

    # Ensure you cannot update a unique field to a value that already exists
    update = client.patch(f"/api/event/risk_level/{obj2.uuid}", json={key: getattr(obj1, key)})
    assert update.status_code == status.HTTP_409_CONFLICT


def test_update_nonexistent_uuid(client):
    update = client.patch(f"/api/event/risk_level/{uuid.uuid4()}", json={"value": "test"})
    assert update.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


@pytest.mark.parametrize(
    "key,initial_value,updated_value",
    [
        ("description", None, "test"),
        ("description", "test", "test"),
        ("value", "test", "test2"),
        ("value", "test", "test"),
    ],
)
def test_update(client, db, key, initial_value, updated_value):
    # Create the object
    obj = helpers.create_event_risk_level(value="test", db=db)

    # Set the initial value
    setattr(obj, key, initial_value)

    # Update it
    update = client.patch(f"/api/event/risk_level/{obj.uuid}", json={key: updated_value})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert getattr(obj, key) == updated_value


def test_update_queue(client, db):
    helpers.create_queue(value="default", db=db)
    helpers.create_queue(value="updated", db=db)

    # Create the object
    obj = helpers.create_event_risk_level(value="test", queues=["default"], db=db)

    # Update it
    update = client.patch(f"/api/event/risk_level/{obj.uuid}", json={"queues": ["updated"]})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert obj.queues[0].value == "updated"
