import pytest
import uuid

from fastapi import status
from db.schemas.analysis import Analysis
from db.schemas.observable_instance import ObservableInstance

from tests.api.node import (
    INVALID_CREATE_FIELDS,
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
        ("description", 123),
        ("description", ""),
        ("event_time", None),
        ("event_time", ""),
        ("event_time", "Monday"),
        ("event_time", "2022-01-01"),
        ("instructions", 123),
        ("instructions", ""),
        ("name", 123),
        ("name", ""),
        ("observable_instances", 123),
        ("observable_instances", ""),
        ("observable_instances", "abc"),
        ("observable_instances", [123]),
        ("observable_instances", [None]),
        ("observable_instances", [""]),
        ("observable_instances", ["abc", 123]),
        ("owner", 123),
        ("owner", ""),
        ("queue", 123),
        ("queue", None),
        ("queue", ""),
        ("tool", 123),
        ("tool", ""),
        ("tool_instance", 123),
        ("tool_instance", ""),
        ("type", 123),
        ("type", None),
        ("type", ""),
        ("uuid", 123),
        ("uuid", None),
        ("uuid", ""),
        ("uuid", "abc"),
    ],
)
def test_create_invalid_fields(client_valid_access_token, key, value):
    create_json = {
        "name": "test alert",
        "queue": "test_queue",
        "observable_instances": [{"type": "o_type", "value": "o_value"}],
        "type": "test_type",
    }
    create_json[key] = value
    create = client_valid_access_token.post("/api/alert/", json=create_json)
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert key in create.text


@pytest.mark.parametrize(
    "key,value",
    INVALID_CREATE_FIELDS,
)
def test_create_invalid_node_fields(client_valid_access_token, key, value):
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            key: value,
            "name": "test alert",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "key",
    [
        ("uuid"),
    ],
)
def test_create_duplicate_unique_fields(client_valid_access_token, db, key):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create an object
    create1_json = {
        "uuid": str(uuid.uuid4()),
        "name": "test alert",
        "queue": "test_queue",
        "observable_instances": [{"type": "o_type", "value": "o_value"}],
        "type": "test_type",
    }
    client_valid_access_token.post("/api/alert/", json=create1_json)

    # Ensure you cannot create another object with the same unique field value
    create2_json = {
        "name": "test alert",
        "queue": "test_queue",
        "observable_instances": [{"type": "o_type", "value": "o_value"}],
        "type": "test_type",
    }
    create2_json[key] = create1_json[key]
    create2 = client_valid_access_token.post("/api/alert/", json=create2_json)
    assert create2.status_code == status.HTTP_409_CONFLICT


def test_create_nonexistent_observable_type(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)

    # Create an object
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "observable_type" in create.text


def test_create_nonexistent_owner(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create an object
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "owner": "johndoe",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "user" in create.text


def test_create_nonexistent_queue(client_valid_access_token, db):
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create an object
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "alert_queue" in create.text


def test_create_nonexistent_tool(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create an object
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "tool": "abc",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "alert_tool" in create.text


def test_create_nonexistent_tool_instance(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create an object
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "tool_instance": "abc",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "alert_tool_instance" in create.text


def test_create_nonexistent_type(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create an object
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "alert_type" in create.text


@pytest.mark.parametrize(
    "key,value",
    NONEXISTENT_FIELDS,
)
def test_create_nonexistent_node_fields(client_valid_access_token, db, key, value):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            key: value,
            "name": "test alert",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("description", None),
        ("description", "test"),
        ("event_time", 1640995200),
        ("event_time", "2022-01-01T00:00:00Z"),
        ("event_time", "2022-01-01 00:00:00"),
        ("event_time", "2022-01-01 00:00:00.000000"),
        ("event_time", "2021-12-31 19:00:00-05:00"),
        ("instructions", None),
        ("instructions", "test"),
        ("uuid", str(uuid.uuid4())),
    ],
)
def test_create_valid_optional_fields(client_valid_access_token, db, key, value):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create the alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            key: value,
            "name": "test alert",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])

    # If the test is for event_time, make sure that the retrieved value matches the proper UTC timestamp
    if key == "event_time" and value:
        assert get.json()[key] == "2022-01-01T00:00:00+00:00"
    else:
        assert get.json()[key] == value


def test_create_valid_owner(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create a user
    helpers.create_user(username="johndoe", db=db)

    # Use the user to create a new alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "owner": "johndoe",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()["owner"]["username"] == "johndoe"


def test_create_valid_tool(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create an alert tool
    helpers.create_alert_tool(value="test_tool", db=db)

    # Use the tool to create a new alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "tool": "test_tool",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()["tool"]["value"] == "test_tool"


def test_create_valid_tool_instance(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create an alert tool instance
    helpers.create_alert_tool_instance(value="test_tool_instance", db=db)

    # Use the tool instance to create a new alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "tool_instance": "test_tool_instance",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()["tool_instance"]["value"] == "test_tool_instance"


def test_create_valid_required_fields(client_valid_access_token, db):
    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create the alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.status_code == 200
    assert get.json()["queue"]["value"] == "test_queue"
    assert get.json()["type"]["value"] == "test_type"

    # There should be 1 analysis associated with the alert
    analyses = db.query(Analysis).all()
    assert len(analyses) == 1
    assert str(analyses[0].alert_uuid) == get.json()["uuid"]

    # There should also be 1 observable instance associated with the alert
    observable_instances = db.query(ObservableInstance).all()
    assert len(observable_instances) == 1
    assert observable_instances[0].observable.type.value == "o_type"
    assert observable_instances[0].observable.value == "o_value"
    assert str(observable_instances[0].alert_uuid) == get.json()["uuid"]
    assert observable_instances[0].parent_uuid == analyses[0].uuid


@pytest.mark.parametrize(
    "values",
    VALID_DIRECTIVES,
)
def test_create_valid_node_directives(client_valid_access_token, db, values):
    for value in values:
        helpers.create_node_directive(value=value, db=db)

    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create the alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "directives": values,
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["directives"]) == len(list(set(values)))


@pytest.mark.parametrize(
    "values",
    VALID_TAGS,
)
def test_create_valid_node_tags(client_valid_access_token, db, values):
    for value in values:
        helpers.create_node_tag(value=value, db=db)

    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create the alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "tags": values,
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["tags"]) == len(list(set(values)))


@pytest.mark.parametrize(
    "value",
    VALID_THREAT_ACTOR,
)
def test_create_valid_node_threat_actor(client_valid_access_token, db, value):
    if value:
        helpers.create_node_threat_actor(value=value, db=db)

    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create the alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "threat_actor": value,
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    if value:
        assert get.json()["threat_actor"]["value"] == value
    else:
        assert get.json()["threat_actor"] is None


@pytest.mark.parametrize(
    "values",
    VALID_THREATS,
)
def test_create_valid_node_threats(client_valid_access_token, db, values):
    for value in values:
        helpers.create_node_threat(value=value, db=db, types=["test_type"])

    helpers.create_alert_queue(value="test_queue", db=db)
    helpers.create_alert_type(value="test_type", db=db)
    helpers.create_observable_type(value="o_type", db=db)

    # Create the alert
    create = client_valid_access_token.post(
        "/api/alert/",
        json={
            "name": "test alert",
            "threats": values,
            "queue": "test_queue",
            "observable_instances": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["threats"]) == len(list(set(values)))
