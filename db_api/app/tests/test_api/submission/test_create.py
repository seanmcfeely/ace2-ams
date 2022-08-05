import pytest
import uuid

from fastapi import status

from db import crud
from db.tests import factory
from tests.test_api.helpers import INVALID_LIST_STRING_VALUES, VALID_LIST_STRING_VALUES


#
# INVALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("analysis_mode_alert", 123),
        ("analysis_mode_alert", ""),
        ("analysis_mode_detect", 123),
        ("analysis_mode_detect", ""),
        ("analysis_mode_event", 123),
        ("analysis_mode_event", ""),
        ("analysis_mode_response", 123),
        ("analysis_mode_response", ""),
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
        ("observables", 123),
        ("observables", ""),
        ("observables", "abc"),
        ("observables", [123]),
        ("observables", [None]),
        ("observables", [""]),
        ("observables", ["abc", 123]),
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
def test_create_invalid_fields(client, key, value):
    create_json = {
        "name": "test alert",
        "queue": "test_queue",
        "observables": [{"type": "o_type", "value": "o_value"}],
        "type": "test_type",
        key: value,
    }

    create = client.post("/api/submission/", json=create_json)
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert key in create.text


@pytest.mark.parametrize(
    "key,values",
    [
        ("tags", INVALID_LIST_STRING_VALUES),
    ],
)
def test_create_invalid_list_fields(client, key, values):
    for value in values:
        create = client.post(
            "/api/submission/",
            json={
                "name": "test alert",
                "queue": "test_queue",
                "observables": [{"type": "o_type", "value": "o_value"}],
                "type": "test_type",
                key: value,
            },
        )
        assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert key in create.json()["detail"][0]["loc"]


def test_create_nonexistent_observable_type(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)

    # Create an object
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "observable_type" in create.text


def test_create_nonexistent_owner(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create an object
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "owner": "johndoe",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "user" in create.text


def test_create_nonexistent_queue(client, db):
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create an object
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "queue": "nonexistent_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "queue" in create.text


def test_create_nonexistent_tool(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create an object
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "tool": "abc",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "submission_tool" in create.text


def test_create_nonexistent_tool_instance(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create an object
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "tool_instance": "abc",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "submission_tool_instance" in create.text


def test_create_nonexistent_type(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create an object
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "submission_type" in create.text


@pytest.mark.parametrize(
    "key",
    [("tags")],
)
def test_create_nonexistent_list_fields(client, db, key):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    create = client.post(
        "/api/submission/",
        json={
            key: ["abc"],
            "name": "test alert",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "abc" in create.text


#
# VALID TESTS
#


def test_create_verify_history(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    submission_uuid = str(uuid.uuid4())
    create = client.post(
        "/api/submission/",
        json={
            "uuid": submission_uuid,
            "name": "test alert",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value", "history_username": "analyst"}],
            "type": "test_type",
            "history_username": "analyst",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Verify the history record
    history = client.get(f"/api/submission/{submission_uuid}/history")
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["action"] == "CREATE"
    assert history.json()["items"][0]["action_by"]["username"] == "analyst"
    assert history.json()["items"][0]["record_uuid"] == submission_uuid
    assert history.json()["items"][0]["field"] is None
    assert history.json()["items"][0]["diff"] is None
    assert history.json()["items"][0]["snapshot"]["name"] == "test alert"

    db_observable = crud.observable.read_by_type_value(type="o_type", value="o_value", db=db)
    history = client.get(f"/api/observable/{db_observable.uuid}/history")
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["action"] == "CREATE"
    assert history.json()["items"][0]["action_by"]["username"] == "analyst"
    assert history.json()["items"][0]["record_uuid"] == str(db_observable.uuid)
    assert history.json()["items"][0]["field"] is None
    assert history.json()["items"][0]["diff"] is None
    assert history.json()["items"][0]["snapshot"]["value"] == "o_value"


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
def test_create_valid_optional_fields(client, db, key, value):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create the alert
    create = client.post(
        "/api/submission/",
        json={
            key: value,
            "name": "test alert",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client.get(create.headers["Content-Location"])

    # If the test is for event_time, make sure that the retrieved value matches the proper UTC timestamp
    if key == "event_time" and value:
        assert get.json()[key] == "2022-01-01T00:00:00+00:00"
    else:
        assert get.json()[key] == value


def test_create_valid_owner(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create a user
    factory.user.create_or_read(username="johndoe", db=db)

    # Use the user to create a new alert
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "owner": "johndoe",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client.get(create.headers["Content-Location"])
    assert get.json()["owner"]["username"] == "johndoe"


def test_create_valid_tool(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create an alert tool
    factory.submission_tool.create_or_read(value="test_tool", db=db)

    # Use the tool to create a new alert
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "tool": "test_tool",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client.get(create.headers["Content-Location"])
    assert get.json()["tool"]["value"] == "test_tool"


def test_create_valid_tool_instance(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create an alert tool instance
    factory.submission_tool_instance.create_or_read(value="test_tool_instance", db=db)

    # Use the tool instance to create a new alert
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "tool_instance": "test_tool_instance",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client.get(create.headers["Content-Location"])
    assert get.json()["tool_instance"]["value"] == "test_tool_instance"


def test_create_valid_required_fields(client, db):
    factory.queue.create_or_read(value="test_queue", db=db)
    factory.submission_type.create_or_read(value="test_type", db=db)
    factory.observable_type.create_or_read(value="o_type", db=db)

    # Create the alert
    create = client.post(
        "/api/submission/",
        json={
            "name": "test alert",
            "queue": "test_queue",
            "observables": [{"type": "o_type", "value": "o_value"}],
            "type": "test_type",
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client.get(create.headers["Content-Location"])
    assert get.status_code == 200
    assert get.json()["queue"]["value"] == "test_queue"
    assert get.json()["type"]["value"] == "test_type"


@pytest.mark.parametrize(
    "key,value_lists,helper_create_func",
    [
        ("tags", VALID_LIST_STRING_VALUES, factory.metadata_tag.create_or_read),
    ],
)
def test_create_valid_list_fields(client, db, key, value_lists, helper_create_func):
    for value_list in value_lists:
        for value in value_list:
            helper_create_func(value=value, db=db)

        factory.queue.create_or_read(value="test_queue", db=db)
        factory.submission_type.create_or_read(value="test_type", db=db)
        factory.observable_type.create_or_read(value="o_type", db=db)

        create = client.post(
            "/api/submission/",
            json={
                key: value_list,
                "name": "test alert",
                "queue": "test_queue",
                "observables": [{"type": "o_type", "value": "o_value"}],
                "type": "test_type",
            },
        )
        assert create.status_code == status.HTTP_201_CREATED

        # Read it back
        get = client.get(create.headers["Content-Location"])
        assert len(get.json()[key]) == len(list(set(value_list)))
