import pytest
import uuid

from dateutil.parser import parse
from fastapi import status

from tests.api.node import INVALID_LIST_STRING_VALUES, VALID_LIST_STRING_VALUES
from tests import helpers


#
# INVALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("description", 123),
        ("description", ""),
        ("disposition", 123),
        ("disposition", ""),
        ("event_uuid", 123),
        ("event_uuid", ""),
        ("event_uuid", "abc"),
        ("event_time", None),
        ("event_time", ""),
        ("event_time", "Monday"),
        ("event_time", "2022-01-01"),
        ("instructions", 123),
        ("instructions", ""),
        ("owner", 123),
        ("owner", ""),
        ("queue", 123),
        ("queue", None),
        ("queue", ""),
    ],
)
def test_update_invalid_fields(client_valid_access_token, key, value):
    update = client_valid_access_token.patch(f"/api/alert/{uuid.uuid4()}", json={key: value})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert key in update.text


@pytest.mark.parametrize(
    "key,values",
    [
        ("tags", INVALID_LIST_STRING_VALUES),
        ("threat_actors", INVALID_LIST_STRING_VALUES),
        ("threats", INVALID_LIST_STRING_VALUES),
    ],
)
def test_update_invalid_node_fields(client_valid_access_token, key, values):
    for value in values:
        update = client_valid_access_token.patch(f"/api/alert/{uuid.uuid4()}", json={key: value})
        assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert key in update.json()["detail"][0]["loc"]


def test_update_invalid_uuid(client_valid_access_token):
    update = client_valid_access_token.patch("/api/alert/1", json={})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_invalid_version(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Make sure you cannot update it using an invalid version. The version is
    # optional, but if given, it must match.
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={"version": str(uuid.uuid4())})
    assert update.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "key,value",
    [
        ("disposition", "abc"),
        ("event_uuid", str(uuid.uuid4())),
        ("owner", "johndoe"),
        ("queue", "abc"),
    ],
)
def test_update_nonexistent_fields(client_valid_access_token, db, key, value):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Make sure you cannot update it to use a nonexistent field value
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={key: value})
    assert update.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "key",
    [("tags"), ("threat_actors"), ("threats")],
)
def test_update_nonexistent_node_fields(client_valid_access_token, db, key):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Make sure you cannot update it to use a nonexistent node field value
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={key: ["abc"]})
    assert update.status_code == status.HTTP_404_NOT_FOUND
    assert "abc" in update.text


def test_update_nonexistent_uuid(client_valid_access_token):
    update = client_valid_access_token.patch(f"/api/alert/{uuid.uuid4()}", json={})
    assert update.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


def test_update_disposition(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)
    initial_version = alert.version

    # Create a user
    helpers.create_user(username="analyst", db=db)

    # Create a disposition
    helpers.create_alert_disposition(value="test", rank=1, db=db)

    # Update the disposition
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={"disposition": "test"})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert alert.disposition.value == "test"
    assert alert.version != initial_version

    # Set it back to None
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={"disposition": None})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert alert.disposition is None


def test_update_event_uuid(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)
    initial_alert_version = alert.version

    # Create an event
    event = helpers.create_event(name="test", db=db)
    initial_event_version = event.version

    # Update the alert to add it to the event
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={"event_uuid": str(event.uuid)})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert alert.event_uuid == event.uuid
    assert alert.version != initial_alert_version

    # By adding the alert to the event, you should be able to see the alert UUID in the event's
    # alert_uuids list even though it was not explicitly added.
    assert event.alert_uuids == [alert.uuid]

    # Additionally, adding the alert to the event should trigger the event to have a new version.
    assert event.version != initial_event_version

    # Set it back to None
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={"event_uuid": None})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert alert.event is None


def test_update_owner(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)
    initial_alert_version = alert.version

    # Create a user
    helpers.create_user(username="johndoe", db=db)

    # Update the owner
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={"owner": "johndoe"})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert alert.owner.username == "johndoe"
    assert alert.version != initial_alert_version

    # Set it back to None
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={"owner": None})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert alert.owner is None


def test_update_queue(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)
    initial_alert_version = alert.version

    # Create a new alert queue
    helpers.create_alert_queue(value="test_queue2", db=db)

    # Update the queue
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={"queue": "test_queue2"})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert alert.queue.value == "test_queue2"
    assert alert.version != initial_alert_version


@pytest.mark.parametrize(
    "key,value_lists,helper_create_func",
    [
        ("tags", VALID_LIST_STRING_VALUES, helpers.create_node_tag),
        ("threat_actors", VALID_LIST_STRING_VALUES, helpers.create_node_threat_actor),
        ("threats", VALID_LIST_STRING_VALUES, helpers.create_node_threat),
    ],
)
def test_update_valid_node_fields(client_valid_access_token, db, key, value_lists, helper_create_func):
    for value_list in value_lists:
        # Create an alert
        alert = helpers.create_alert(db=db)
        initial_alert_version = alert.version

        for value in value_list:
            helper_create_func(value=value, db=db)

        helpers.create_alert_queue(value="test_queue", db=db)
        helpers.create_alert_type(value="test_type", db=db)
        helpers.create_observable_type(value="o_type", db=db)

        # Update the alert
        update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={key: value_list})
        assert update.status_code == status.HTTP_204_NO_CONTENT
        assert len(getattr(alert, key)) == len(set(value_list))
        assert alert.version != initial_alert_version


@pytest.mark.parametrize(
    "key,initial_value,updated_value",
    [
        ("description", None, "test"),
        ("description", "test", None),
        ("description", "test", "test"),
        ("event_time", "2021-01-01T00:00:00+00:00", 1640995200),
        ("event_time", "2021-01-01T00:00:00+00:00", "2022-01-01T00:00:00Z"),
        ("event_time", "2021-01-01T00:00:00+00:00", "2022-01-01 00:00:00"),
        ("event_time", "2021-01-01T00:00:00+00:00", "2022-01-01 00:00:00.000000"),
        ("event_time", "2021-01-01T00:00:00+00:00", "2021-12-31 19:00:00-05:00"),
        ("instructions", None, "test"),
        ("instructions", "test", None),
        ("instructions", "test", "test"),
    ],
)
def test_update(client_valid_access_token, db, key, initial_value, updated_value):
    # Create an alert
    alert = helpers.create_alert(db=db)
    initial_alert_version = alert.version

    # Set the initial value on the alert
    setattr(alert, key, initial_value)
    assert getattr(alert, key) == initial_value

    # Update it
    update = client_valid_access_token.patch(f"/api/alert/{alert.uuid}", json={key: updated_value})
    assert update.status_code == status.HTTP_204_NO_CONTENT

    if key == "event_time":
        assert alert.event_time == parse("2022-01-01T00:00:00+00:00")
    else:
        assert getattr(alert, key) == updated_value

    assert alert.version != initial_alert_version
