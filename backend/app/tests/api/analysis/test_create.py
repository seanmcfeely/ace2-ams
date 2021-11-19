import json
import pytest
import uuid

from fastapi import status

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
        ("analysis_module_type", 123),
        ("analysis_module_type", ""),
        ("analysis_module_type", "abc"),
        ("details", 123),
        ("details", ""),
        ("details", "abc"),
        ("details", []),
        ("error_message", 123),
        ("error_message", ""),
        ("stack_trace", 123),
        ("stack_trace", ""),
        ("summary", 123),
        ("summary", ""),
        ("uuid", 123),
        ("uuid", None),
        ("uuid", ""),
        ("uuid", "abc"),
    ],
)
def test_create_invalid_fields(client_valid_access_token, key, value):
    create = client_valid_access_token.post("/api/analysis/", json={key: value})
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "key,value",
    INVALID_CREATE_FIELDS,
)
def test_create_invalid_node_fields(client_valid_access_token, key, value):
    create = client_valid_access_token.post("/api/analysis/", json={key: value})
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "key",
    [
        ("uuid"),
    ],
)
def test_create_duplicate_unique_fields(client_valid_access_token, key):
    # Create an object
    create1_json = {"uuid": str(uuid.uuid4())}
    client_valid_access_token.post("/api/analysis/", json=create1_json)

    # Ensure you cannot create another object with the same unique field value
    create2_json = {}
    create2_json[key] = create1_json[key]
    create2 = client_valid_access_token.post("/api/analysis/", json=create2_json)
    assert create2.status_code == status.HTTP_409_CONFLICT


def test_create_nonexistent_analysis_module_type(client_valid_access_token):
    create = client_valid_access_token.post("/api/analysis/", json={"analysis_module_type": str(uuid.uuid4())})
    assert create.status_code == status.HTTP_404_NOT_FOUND


def test_create_nonexistent_parent_observable_uuid(client_valid_access_token):
    create = client_valid_access_token.post("/api/analysis/", json={"parent_observable_uuid": str(uuid.uuid4())})
    assert create.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "key,value",
    NONEXISTENT_FIELDS,
)
def test_create_nonexistent_node_fields(client_valid_access_token, key, value):
    create = client_valid_access_token.post("/api/analysis/", json={key: value})
    assert create.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("details", None),
        ("details", "{}"),
        ("details", '{"foo": "bar"}'),
        ("error_message", None),
        ("error_message", "test"),
        ("stack_trace", None),
        ("stack_trace", "test"),
        ("summary", None),
        ("summary", "test"),
        ("uuid", str(uuid.uuid4())),
    ],
)
def test_create_valid_optional_fields(client_valid_access_token, key, value):
    # Create the object
    create = client_valid_access_token.post("/api/analysis/", json={key: value})
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])

    # If the test is for details, make sure the JSON form of the supplied string matches
    if key == "details" and value:
        assert get.json()[key] == json.loads(value)
    else:
        assert get.json()[key] == value


def test_create_valid_analysis_module_type(client_valid_access_token, db):
    # Create an analysis module type
    analysis_module_type = helpers.create_analysis_module_type(value="test", db=db)

    # Use the analysis module type to create a new analysis
    create = client_valid_access_token.post(
        "/api/analysis/", json={"analysis_module_type": str(analysis_module_type.uuid)}
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()["analysis_module_type"]["uuid"] == str(analysis_module_type.uuid)


def test_create_valid_parent_observable_uuid(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable instance
    observable_instance = helpers.create_observable_instance(
        type="test_type", value="test", alert=alert, parent_analysis=alert.analysis, db=db
    )
    initial_observable_instance_version = observable_instance.version

    # Use the observable instance as the parent for a new analysis
    child_analysis_uuid = uuid.uuid4()
    create = client_valid_access_token.post(
        "/api/analysis/",
        json={
            "parent_observable_uuid": str(observable_instance.uuid),
            "uuid": str(child_analysis_uuid),
        },
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()["parent_observable_uuid"] == str(observable_instance.uuid)

    # By creating the analysis and setting its parent_observable_uuid, you should be
    # able to read that observable instance back and see the analysis listed in its
    # performed_analysis_uuids list even though it was not explictly added.
    assert observable_instance.performed_analysis_uuids == [child_analysis_uuid]

    # Additionally, adding the child analysis to the observable instance should trigger
    # the observable instance to get a new version.
    assert observable_instance.version != initial_observable_instance_version


def test_create_valid_required_fields(client_valid_access_token):
    # Create the object
    create = client_valid_access_token.post("/api/analysis/", json={})
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back, but since there are no required fields to create the analysis, there is nothing to verify.
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.status_code == 200


@pytest.mark.parametrize(
    "values",
    VALID_DIRECTIVES,
)
def test_create_valid_node_directives(client_valid_access_token, db, values):
    # Create the directives
    for value in values:
        helpers.create_node_directive(value=value, db=db)

    # Create the node
    create = client_valid_access_token.post("/api/analysis/", json={"directives": values})
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["directives"]) == len(list(set(values)))


@pytest.mark.parametrize(
    "values",
    VALID_TAGS,
)
def test_create_valid_node_tags(client_valid_access_token, db, values):
    # Create the tags
    for value in values:
        helpers.create_node_tag(value=value, db=db)

    # Create the node
    create = client_valid_access_token.post("/api/analysis/", json={"tags": values})
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["tags"]) == len(list(set(values)))


@pytest.mark.parametrize(
    "value",
    VALID_THREAT_ACTOR,
)
def test_create_valid_node_threat_actor(client_valid_access_token, db, value):
    # Create the threat actor
    if value:
        helpers.create_node_threat_actor(value=value, db=db)

    # Create the node
    create = client_valid_access_token.post("/api/analysis/", json={"threat_actor": value})
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
    # Create the threats
    for value in values:
        helpers.create_node_threat(value=value, types=["test_type"], db=db)

    # Create the node
    create = client_valid_access_token.post("/api/analysis/", json={"threats": values})
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["threats"]) == len(set(values))