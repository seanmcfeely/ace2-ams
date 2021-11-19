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
        ("alert_uuid", 123),
        ("alert_uuid", None),
        ("alert_uuid", ""),
        ("alert_uuid", "abc"),
        ("context", 123),
        ("context", ""),
        ("parent_analysis_uuid", 123),
        ("parent_analysis_uuid", None),
        ("parent_analysis_uuid", ""),
        ("parent_analysis_uuid", "abc"),
        ("performed_analysis_uuids", 123),
        ("performed_analysis_uuids", "abc"),
        ("performed_analysis_uuids", [123]),
        ("performed_analysis_uuids", [None]),
        ("performed_analysis_uuids", [""]),
        ("performed_analysis_uuids", ["abc"]),
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
        ("uuid", 123),
        ("uuid", None),
        ("uuid", ""),
        ("uuid", "abc"),
        ("value", 123),
        ("value", None),
        ("value", ""),
    ],
)
def test_create_invalid_fields(client_valid_access_token, key, value):
    create_json = {
        key: value,
        "alert_uuid": str(uuid.uuid4()),
        "parent_analysis_uuid": str(uuid.uuid4()),
        "type": "test_type",
        "value": "test",
    }
    create_json[key] = value
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert key in create.text


@pytest.mark.parametrize(
    "key,value",
    INVALID_CREATE_FIELDS,
)
def test_create_invalid_node_fields(client_valid_access_token, key, value):
    create_json = {
        key: value,
        "alert_uuid": str(uuid.uuid4()),
        "parent_analysis_uuid": str(uuid.uuid4()),
        "type": "test_type",
        "value": "test",
    }
    create_json[key] = value
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_duplicate_uuid(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create an object
    create_json = {
        "uuid": str(uuid.uuid4()),
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "value": "test",
    }
    client_valid_access_token.post("/api/observable/instance/", json=[create_json])

    # Ensure you cannot create another object with the same UUID
    create2 = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create2.status_code == status.HTTP_409_CONFLICT


def test_create_nonexistent_alert(client_valid_access_token, db):
    # Create an analysis
    analysis = helpers.create_analysis(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Ensure you cannot create an observable instance with a nonexistent alert
    nonexistent_alert_uuid = str(uuid.uuid4())
    create_json = {
        "alert_uuid": nonexistent_alert_uuid,
        "parent_analysis_uuid": str(analysis.uuid),
        "type": "test_type",
        "value": "test",
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert nonexistent_alert_uuid in create.text


def test_create_nonexistent_analysis(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Ensure you cannot create an observable instance with a nonexistent analysis
    nonexistent_analysis_uuid = str(uuid.uuid4())
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": nonexistent_analysis_uuid,
        "type": "test_type",
        "value": "test",
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert nonexistent_analysis_uuid in create.text


def test_create_nonexistent_performed_analysis(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Ensure you cannot create an observable instance with a nonexistent performed analysis
    nonexistent_analysis_uuid = str(uuid.uuid4())
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "performed_analysis_uuids": [nonexistent_analysis_uuid],
        "type": "test_type",
        "value": "test",
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert nonexistent_analysis_uuid in create.text


def test_create_nonexistent_redirection(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Ensure you cannot create an observable instance with a nonexistent redirection target
    nonexistent_redirection_uuid = str(uuid.uuid4())
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "redirection_uuid": nonexistent_redirection_uuid,
        "type": "test_type",
        "value": "test",
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert nonexistent_redirection_uuid in create.text


def test_create_nonexistent_type(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Ensure you cannot create an observable instance with a nonexistent type
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "abc",
        "value": "test",
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_404_NOT_FOUND
    assert "abc" in create.text


@pytest.mark.parametrize(
    "key,value",
    NONEXISTENT_FIELDS,
)
def test_create_nonexistent_node_fields(client_valid_access_token, db, key, value):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Ensure you cannot create an observable instance with a nonexistent type
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "value": "test",
    }
    create_json[key] = value
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


def test_create_bulk(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)
    initial_alert_version = alert.version
    initial_analysis_version = alert.analysis.version

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create some observable instances
    observable_instances = []
    for i in range(3):
        observable_uuid = str(uuid.uuid4())
        observable_instances.append(
            {
                "alert_uuid": str(alert.uuid),
                "parent_analysis_uuid": str(alert.analysis_uuid),
                "type": "test_type",
                "uuid": observable_uuid,
                "value": f"test{i}",
            }
        )
    create = client_valid_access_token.post("/api/observable/instance/", json=observable_instances)
    assert create.status_code == status.HTTP_201_CREATED

    # The analysis should have 3 discovered observable instance UUIDs.
    assert len(alert.analysis.discovered_observable_uuids) == 3

    # Additionally, creating an observable instance should trigger the alert and analysis to get a new version.
    assert alert.version != initial_alert_version
    assert alert.analysis.version != initial_analysis_version


@pytest.mark.parametrize(
    "key,value",
    [
        ("context", None),
        ("context", "test"),
        ("time", 1640995200),
        ("time", "2022-01-01T00:00:00Z"),
        ("time", "2022-01-01 00:00:00"),
        ("time", "2022-01-01 00:00:00.000000"),
        ("time", "2021-12-31 19:00:00-05:00"),
        ("uuid", str(uuid.uuid4())),
    ],
)
def test_create_valid_optional_fields(client_valid_access_token, db, key, value):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create the observable instance
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "value": "test",
    }
    create_json[key] = value
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])

    # If the test is for time, make sure that the retrieved value matches the proper UTC timestamp
    if key == "time" and value:
        assert get.json()[key] == "2022-01-01T00:00:00+00:00"
    else:
        assert get.json()[key] == value


def test_create_valid_performed_analysis_uuids(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create a child analysis for the observable instance
    child_analysis = helpers.create_analysis(db=db)
    initial_child_analysis_version = child_analysis.version

    # Create the observable instance
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "performed_analysis_uuids": [str(child_analysis.uuid)],
        "type": "test_type",
        "value": "test",
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()["performed_analysis_uuids"] == [str(child_analysis.uuid)]

    # By creating the observable instance and setting its performed_analysis_uuids, you should
    # be able to see the observable instance listed as the analysis' parent_observable_uuid even
    # though it was not explicitly added.
    assert str(child_analysis.parent_observable_uuid) == get.json()["uuid"]

    # Additionally, adding the observable instance as the parent should trigger the analysis to have a new version.
    assert child_analysis.version != initial_child_analysis_version


def test_create_valid_redirection(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create an observable instance
    observable_instance_uuid = str(uuid.uuid4())
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "uuid": observable_instance_uuid,
        "value": "test",
    }
    client_valid_access_token.post("/api/observable/instance/", json=[create_json])

    # Create another observable instance that redirects to the previously created one
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "redirection_uuid": observable_instance_uuid,
        "type": "test_type",
        "value": "test",
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()["redirection_uuid"] == observable_instance_uuid


def test_create_valid_required_fields(client_valid_access_token, db):
    # Create an alert
    alert = helpers.create_alert(db=db)
    initial_alert_version = alert.version
    initial_analysis_version = alert.analysis.version

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create an observable instance
    observable_uuid = uuid.uuid4()
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "uuid": str(observable_uuid),
        "value": "test",
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.status_code == 200
    assert get.json()["alert_uuid"] == str(alert.uuid)
    assert get.json()["parent_analysis_uuid"] == str(alert.analysis_uuid)
    assert get.json()["observable"]["type"]["value"] == "test_type"
    assert get.json()["uuid"] == str(observable_uuid)
    assert get.json()["observable"]["value"] == "test"

    # You should see this observable instance in the analysis' discovered_observable_uuids list
    # even though it was not explicitly added.
    assert alert.analysis.discovered_observable_uuids == [observable_uuid]

    # Additionally, creating an observable instance should trigger the alert and analysis to get a new version.
    assert alert.version != initial_alert_version
    assert alert.analysis.version != initial_analysis_version


@pytest.mark.parametrize(
    "values",
    VALID_DIRECTIVES,
)
def test_create_valid_node_directives(client_valid_access_token, db, values):
    # Create the directives
    for value in values:
        helpers.create_node_directive(value=value, db=db)

    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create an observable instance
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "value": "test",
        "directives": values,
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["directives"]) == len(set(values))


@pytest.mark.parametrize(
    "values",
    VALID_TAGS,
)
def test_create_valid_node_tags(client_valid_access_token, db, values):
    # Create the tags
    for value in values:
        helpers.create_node_tag(value=value, db=db)

    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create an observable instance
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "value": "test",
        "tags": values,
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
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

    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create an observable instance
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "value": "test",
        "threat_actor": value,
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
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
        helpers.create_node_threat(value=value, db=db)

    # Create an alert
    alert = helpers.create_alert(db=db)

    # Create an observable type
    helpers.create_observable_type(value="test_type", db=db)

    # Create an observable instance
    create_json = {
        "alert_uuid": str(alert.uuid),
        "parent_analysis_uuid": str(alert.analysis_uuid),
        "type": "test_type",
        "value": "test",
        "threats": values,
    }
    create = client_valid_access_token.post("/api/observable/instance/", json=[create_json])
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["threats"]) == len(set(values))