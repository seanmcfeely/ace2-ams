import pytest
import uuid

from datetime import datetime
from dateutil.parser import parse
from fastapi import status

from tests.api.node import (
    INVALID_UPDATE_FIELDS,
    NONEXISTENT_FIELDS,
    VALID_DIRECTIVES,
    VALID_TAGS,
    VALID_THREAT_ACTOR,
    VALID_THREATS,
)
from tests import helpers


#
# INVALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("context", 123),
        ("context", ""),
        ("expires_on", ""),
        ("expires_on", "Monday"),
        ("expires_on", "2022-01-01"),
        ("for_detection", 123),
        ("for_detection", None),
        ("for_detection", "True"),
        ("redirection_uuid", 123),
        ("redirection_uuid", ""),
        ("redirection_uuid", "abc"),
        ("time", None),
        ("time", ""),
        ("time", "Monday"),
        ("time", "2022-01-01"),
        ("type", 123),
        ("type", None),
        ("type", ""),
        ("value", 123),
        ("value", None),
        ("value", ""),
    ],
)
def test_update_invalid_fields(client_valid_access_token, key, value):
    update = client_valid_access_token.patch(f"/api/observable/{uuid.uuid4()}", json={key: value})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert len(update.json()["detail"]) == 1
    assert key in update.json()["detail"][0]["loc"]


@pytest.mark.parametrize(
    "key,value",
    INVALID_UPDATE_FIELDS,
)
def test_update_invalid_node_fields(client_valid_access_token, key, value):
    update = client_valid_access_token.patch(
        f"/api/observable/{uuid.uuid4()}",
        json={key: value},
    )
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert len(update.json()["detail"]) == 1
    assert key in update.json()["detail"][0]["loc"]


def test_update_invalid_uuid(client_valid_access_token):
    update = client_valid_access_token.patch("/api/observable/1", json={"types": ["test_type"], "value": "test"})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_invalid_version(client_valid_access_token, db):
    # Create an observable
    obj = helpers.create_observable(type="test_type", value="test", db=db)

    # Make sure you cannot update it using an invalid version. The version is
    # optional, but if given, it must match.
    update = client_valid_access_token.patch(f"/api/observable/{obj.uuid}", json={"version": str(uuid.uuid4())})
    assert update.status_code == status.HTTP_409_CONFLICT


def test_update_duplicate_type_value(client_valid_access_token, db):
    # Create some observables
    obj1 = helpers.create_observable(type="test_type", value="test", db=db)
    obj2 = helpers.create_observable(type="test_type", value="test2", db=db)

    # Ensure you cannot update an observable to have a duplicate type+value combination
    update = client_valid_access_token.patch(f"/api/observable/{obj2.uuid}", json={"value": obj1.value})
    assert update.status_code == status.HTTP_409_CONFLICT


def test_update_nonexistent_redirection_uuid(client_valid_access_token, db):
    # Create an observable
    obj = helpers.create_observable(type="test_type", value="test", db=db)

    # Make sure you cannot update it to use a nonexistent redirection UUID
    update = client_valid_access_token.patch(
        f"/api/observable/{obj.uuid}",
        json={"redirection_uuid": str(uuid.uuid4())},
    )
    assert update.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "key,value",
    NONEXISTENT_FIELDS,
)
def test_update_nonexistent_node_fields(client_valid_access_token, db, key, value):
    # Create an observable
    obj = helpers.create_observable(type="test_type", value="test", db=db)

    # Make sure you cannot update it to use a nonexistent node field value
    update = client_valid_access_token.patch(f"/api/observable/{obj.uuid}", json={key: value})
    assert update.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_uuid(client_valid_access_token):
    update = client_valid_access_token.patch(
        f"/api/observable/{uuid.uuid4()}", json={"type": "test_type", "value": "test"}
    )
    assert update.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


def test_update_type(client_valid_access_token, db):
    # Create the object
    obj = helpers.create_observable(type="test_type", value="test", db=db)
    assert obj.type.value == "test_type"

    # Create a new observable type
    helpers.create_observable_type(value="test_type2", db=db)

    # Update it
    update = client_valid_access_token.patch(f"/api/observable/{obj.uuid}", json={"type": "test_type2"})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert obj.type.value == "test_type2"


def test_update_redirection_uuid(client_valid_access_token, db):
    # Create an observable
    obj1 = helpers.create_observable(type="test_type", value="test", db=db)
    initial_observable_version = obj1.version
    assert obj1.redirection is None

    # Create a second observable to use for redirection
    obj2 = helpers.create_observable(type="test_type", value="test2", db=db)

    # Update the redirection UUID
    update = client_valid_access_token.patch(f"/api/observable/{obj1.uuid}", json={"redirection_uuid": str(obj2.uuid)})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert obj1.redirection_uuid == obj2.uuid
    assert obj1.version != initial_observable_version


@pytest.mark.parametrize(
    "values",
    VALID_DIRECTIVES,
)
def test_update_valid_node_directives(client_valid_access_token, db, values):
    # Create an observable
    obj = helpers.create_observable(type="test_type", value="test", db=db)
    initial_observable_version = obj.version
    assert obj.directives == []

    # Create the directives
    for value in values:
        helpers.create_node_directive(value=value, db=db)

    # Update the node
    update = client_valid_access_token.patch(f"/api/observable/{obj.uuid}", json={"directives": values})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert len(obj.directives) == len(set(values))
    assert obj.version != initial_observable_version


@pytest.mark.parametrize(
    "values",
    VALID_TAGS,
)
def test_update_valid_node_tags(client_valid_access_token, db, values):
    # Create an observable
    obj = helpers.create_observable(type="test_type", value="test", db=db)
    initial_observable_version = obj.version
    assert obj.tags == []

    # Create the tags
    for value in values:
        helpers.create_node_tag(value=value, db=db)

    # Update the node
    update = client_valid_access_token.patch(f"/api/observable/{obj.uuid}", json={"tags": values})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert len(obj.tags) == len(set(values))
    assert obj.version != initial_observable_version


@pytest.mark.parametrize(
    "value",
    VALID_THREAT_ACTOR,
)
def test_update_valid_node_threat_actor(client_valid_access_token, db, value):
    # Create an observable
    obj = helpers.create_observable(type="test_type", value="test", db=db)
    initial_observable_version = obj.version
    assert obj.threat_actor is None

    # Create the threat actor
    if value:
        helpers.create_node_threat_actor(value=value, db=db)

    # Update the node
    update = client_valid_access_token.patch(f"/api/observable/{obj.uuid}", json={"threat_actor": value})
    assert update.status_code == status.HTTP_204_NO_CONTENT

    if value:
        assert obj.threat_actor.value == value
    else:
        assert obj.threat_actor is None

    assert obj.version != initial_observable_version


@pytest.mark.parametrize(
    "values",
    VALID_THREATS,
)
def test_update_valid_node_threats(client_valid_access_token, db, values):
    # Create an observable
    obj = helpers.create_observable(type="test_type", value="test", db=db)
    initial_observable_version = obj.version
    assert obj.threats == []

    # Create the threats
    for value in values:
        helpers.create_node_threat(value=value, types=["test_type"], db=db)

    # Update the node
    update = client_valid_access_token.patch(f"/api/observable/{obj.uuid}", json={"threats": values})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert len(obj.threats) == len(set(values))
    assert obj.version != initial_observable_version


@pytest.mark.parametrize(
    "key,initial_value,updated_value",
    [
        ("context", None, "test"),
        ("context", "test", None),
        ("context", "test", "test"),
        ("expires_on", 1640995200, 1640995200),
        ("expires_on", None, 1640995200),
        ("expires_on", None, "2022-01-01T00:00:00Z"),
        ("expires_on", None, "2022-01-01 00:00:00"),
        ("expires_on", None, "2022-01-01 00:00:00.000000"),
        ("expires_on", None, "2021-12-31 19:00:00-05:00"),
        ("expires_on", 1640995200, None),
        ("for_detection", True, False),
        ("for_detection", True, True),
        ("time", "2021-01-01T00:00:00+00:00", 1640995200),
        ("time", "2021-01-01T00:00:00+00:00", "2022-01-01T00:00:00Z"),
        ("time", "2021-01-01T00:00:00+00:00", "2022-01-01 00:00:00"),
        ("time", "2021-01-01T00:00:00+00:00", "2022-01-01 00:00:00.000000"),
        ("time", "2021-01-01T00:00:00+00:00", "2021-12-31 19:00:00-05:00"),
        ("value", "test", "test2"),
        ("value", "test", "test"),
    ],
)
def test_update(client_valid_access_token, db, key, initial_value, updated_value):
    # Create the object
    obj = helpers.create_observable(type="test_type", value="test", db=db)

    # Set the initial value
    if key == "expires_on" and initial_value:
        setattr(obj, key, datetime.utcfromtimestamp(initial_value))
    else:
        setattr(obj, key, initial_value)

    # Update it
    update = client_valid_access_token.patch(f"/api/observable/{obj.uuid}", json={key: updated_value})
    assert update.status_code == status.HTTP_204_NO_CONTENT

    # If the test is for expires_on, make sure that the retrieved value matches the proper UTC timestamp
    if key == "expires_on" and updated_value:
        assert obj.expires_on == parse("2022-01-01T00:00:00+00:00")
    elif key == "time" and updated_value:
        assert obj.time == parse("2022-01-01T00:00:00+00:00")
    else:
        assert getattr(obj, key) == updated_value
