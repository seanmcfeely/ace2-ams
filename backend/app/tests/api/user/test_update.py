import pytest
import uuid

from fastapi import status

from core.auth import verify_password
from db import crud
from db.schemas.history import History
from db.schemas.user import UserHistory
from tests import helpers


#
# INVALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("default_alert_queue", 123),
        ("default_alert_queue", None),
        ("default_alert_queue", ""),
        ("default_event_queue", 123),
        ("default_event_queue", None),
        ("default_event_queue", ""),
        ("display_name", 123),
        ("display_name", None),
        ("display_name", ""),
        ("email", 123),
        ("email", None),
        ("email", ""),
        ("email", "johndoe"),
        ("email", "johndoe@test"),
        ("enabled", 123),
        ("enabled", None),
        ("enabled", "True"),
        ("password", 123),
        ("password", None),
        ("password", ""),
        ("password", "abc"),
        ("roles", 123),
        ("roles", None),
        ("roles", "test_role"),
        ("roles", [123]),
        ("roles", [None]),
        ("roles", [""]),
        ("roles", ["abc", 123]),
        ("timezone", 123),
        ("timezone", None),
        ("timezone", ""),
        ("timezone", "Mars/Jezero"),
        ("training", 123),
        ("training", None),
        ("training", "True"),
        ("username", 123),
        ("username", None),
        ("username", ""),
    ],
)
def test_update_invalid_fields(client_valid_access_token, key, value):
    update = client_valid_access_token.patch(f"/api/user/{uuid.uuid4()}", json={key: value})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_invalid_uuid(client_valid_access_token):
    update = client_valid_access_token.patch("/api/user/1", json={"value": "test"})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "key",
    [
        ("email"),
        ("username"),
    ],
)
def test_update_duplicate_unique_fields(client_valid_access_token, db, key):
    # Create some users
    obj1 = helpers.create_user(username="johndoe", email="johndoe@test.com", db=db)
    obj2 = helpers.create_user(username="janedoe", email="janedoe@test.com", db=db)

    # Ensure you cannot update a unique field to a value that already exists
    update = client_valid_access_token.patch(f"/api/user/{obj2.uuid}", json={key: getattr(obj1, key)})
    assert update.status_code == status.HTTP_409_CONFLICT


def test_update_nonexistent_uuid(client_valid_access_token):
    update = client_valid_access_token.patch(f"/api/user/{uuid.uuid4()}", json={"display_name": "test"})
    assert update.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


def test_update_valid_alert_queue(client_valid_access_token, db):
    # Create a user
    obj = helpers.create_user(username="johndoe", alert_queue="test_queue", db=db)
    assert obj.default_alert_queue.value == "test_queue"

    # Create the new alert queue
    helpers.create_alert_queue(value="test_queue2", db=db)

    # Update it
    update = client_valid_access_token.patch(f"/api/user/{obj.uuid}", json={"default_alert_queue": "test_queue2"})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert obj.default_alert_queue.value == "test_queue2"

    # Verify the history
    history: list[History] = crud.read_history_records(UserHistory, record_uuid=obj.uuid, db=db)
    assert len(history) == 1
    assert history[0].action == "UPDATE"
    assert history[0].action_by == "analyst"
    assert history[0].field == "default_alert_queue"
    assert history[0].diff["old_value"] == "test_queue"
    assert history[0].diff["new_value"] == "test_queue2"


def test_update_valid_event_queue(client_valid_access_token, db):
    # Create a user
    obj = helpers.create_user(username="johndoe", event_queue="test_queue", db=db)
    assert obj.default_event_queue.value == "test_queue"

    # Create the new event queue
    helpers.create_event_queue(value="test_queue2", db=db)

    # Update it
    update = client_valid_access_token.patch(f"/api/user/{obj.uuid}", json={"default_event_queue": "test_queue2"})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert obj.default_event_queue.value == "test_queue2"

    # Verify the history
    history: list[History] = crud.read_history_records(UserHistory, record_uuid=obj.uuid, db=db)
    assert len(history) == 1
    assert history[0].action == "UPDATE"
    assert history[0].action_by == "analyst"
    assert history[0].field == "default_event_queue"
    assert history[0].diff["old_value"] == "test_queue"
    assert history[0].diff["new_value"] == "test_queue2"


@pytest.mark.parametrize(
    "values",
    [
        (["new_role"]),
        (["new_role1", "new_role2"]),
    ],
)
def test_update_valid_roles(client_valid_access_token, db, values):
    # Create a user
    initial_roles = ["test_role1", "test_role2", "test_role3"]
    obj = helpers.create_user(username="johndoe", roles=initial_roles, db=db)
    assert len(obj.roles) == len(initial_roles)

    # Create the new user roles
    for value in values:
        helpers.create_user_role(value=value, db=db)

    # Update it
    update = client_valid_access_token.patch(f"/api/user/{obj.uuid}", json={"roles": values})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert len(obj.roles) == len(values)

    # Verify the history
    history: list[History] = crud.read_history_records(UserHistory, record_uuid=obj.uuid, db=db)
    assert len(history) == 1
    assert history[0].action == "UPDATE"
    assert history[0].action_by == "analyst"
    assert history[0].field == "roles"
    assert history[0].diff["old_value"] is None
    assert history[0].diff["new_value"] is None
    assert history[0].diff["added_to_list"] == values
    assert history[0].diff["removed_from_list"] == initial_roles


@pytest.mark.parametrize(
    "key,initial_value,updated_value",
    [
        ("display_name", "John Doe", "Johnathan Doe"),
        ("display_name", "John Doe", "John Doe"),
        ("email", "john@test.com", "johnathan@test.com"),
        ("email", "john@test.com", "john@test.com"),
        ("enabled", True, False),
        ("enabled", False, True),
        ("timezone", "UTC", "America/New_York"),
        ("timezone", "UTC", "UTC"),
        ("training", True, False),
        ("training", False, True),
        ("username", "johndoe", "johnathandoe"),
        ("username", "johndoe", "johndoe"),
    ],
)
def test_update(client_valid_access_token, db, key, initial_value, updated_value):
    # Create a user
    obj = helpers.create_user(username="johndoe", db=db)

    # Set the initial value
    setattr(obj, key, initial_value)

    # Update it
    update = client_valid_access_token.patch(f"/api/user/{obj.uuid}", json={key: updated_value})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert getattr(obj, key) == updated_value

    # Verify the history
    history: list[History] = crud.read_history_records(UserHistory, record_uuid=obj.uuid, db=db)
    assert len(history) == 1
    assert history[0].action == "UPDATE"
    assert history[0].action_by == "analyst"
    assert history[0].field == key
    assert history[0].diff["old_value"] == initial_value
    assert history[0].diff["new_value"] == updated_value


@pytest.mark.parametrize(
    "initial_value,updated_value",
    [
        ("abcd1234", "wxyz6789"),
        ("abcd1234", "abcd1234"),
    ],
)
def test_update_password(client_valid_access_token, db, initial_value, updated_value):
    # Create a user
    obj = helpers.create_user(username="johndoe", password=initial_value, db=db)
    initial_password_hash = obj.password

    # Make sure the initial password validates against its hash
    assert verify_password(initial_value, initial_password_hash) is True

    # Update it
    update = client_valid_access_token.patch(f"/api/user/{obj.uuid}", json={"password": updated_value})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert obj.password != initial_password_hash
    assert verify_password(updated_value, obj.password) is True

    # Verify the history
    history: list[History] = crud.read_history_records(UserHistory, record_uuid=obj.uuid, db=db)
    assert len(history) == 1
    assert history[0].action == "UPDATE"
    assert history[0].action_by == "analyst"
    assert history[0].field == "password"
    assert history[0].diff["old_value"] is None
    assert history[0].diff["new_value"] is None
