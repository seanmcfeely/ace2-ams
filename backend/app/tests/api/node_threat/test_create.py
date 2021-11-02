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
        ("types", 123),
        ("types", None),
        ("types", "test_type"),
        ("types", [123]),
        ("types", [None]),
        ("types", [""]),
        ("types", ["abc", 123]),
        ("types", []),
        ("uuid", 123),
        ("uuid", None),
        ("uuid", ""),
        ("uuid", "abc"),
        ("uuid", ""),
        ("value", 123),
        ("value", None),
        ("value", ""),
    ],
)
def test_create_invalid_fields(client_valid_access_token, key, value):
    create_json = {"types": ["test_type"], "value": "test"}
    create_json[key] = value
    create = client_valid_access_token.post("/api/node/threat/", json=create_json)
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "key",
    [
        ("uuid"),
        ("value"),
    ],
)
def test_create_duplicate_unique_fields(client_valid_access_token, db, key):
    # Create a node threat type
    helpers.create_node_threat_type(value="test_type", db=db)

    # Create an object
    create1_json = {"types": ["test_type"], "uuid": str(uuid.uuid4()), "value": "test"}
    client_valid_access_token.post("/api/node/threat/", json=create1_json)

    # Ensure you cannot create another object with the same unique field value
    create2_json = {"types": ["test_type"], "value": "test2"}
    create2_json[key] = create1_json[key]
    create2 = client_valid_access_token.post("/api/node/threat/", json=create2_json)
    assert create2.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "key",
    [
        ("types"),
        ("value"),
    ],
)
def test_create_missing_required_fields(client_valid_access_token, key):
    create_json = {"types": ["test_type"], "value": "test"}
    del create_json[key]
    create = client_valid_access_token.post("/api/node/threat/", json=create_json)
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_nonexistent_type(client_valid_access_token):
    create = client_valid_access_token.post("/api/node/threat/", json={"types": ["test_type"], "value": "test"})
    assert create.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("description", None),
        ("description", "test"),
        ("uuid", str(uuid.uuid4())),
    ],
)
def test_create_valid_optional_fields(client_valid_access_token, db, key, value):
    # Create a node threat type
    helpers.create_node_threat_type(value="test_type", db=db)

    # Create the object
    create = client_valid_access_token.post(
        "/api/node/threat/", json={key: value, "types": ["test_type"], "value": "test"}
    )
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()[key] == value


@pytest.mark.parametrize(
    "values,list_length",
    [
        (["test_type"], 1),
        (["test_type1", "test_type2"], 2),
        (["test_type", "test_type"], 1),
    ],
)
def test_create_valid_types(client_valid_access_token, db, values, list_length):
    # Create the node threat types
    for value in values:
        helpers.create_node_threat_type(value=value, db=db)

    # Create the object
    create = client_valid_access_token.post("/api/node/threat/", json={"types": values, "value": "test"})
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert len(get.json()["types"]) == list_length


def test_create_valid_required_fields(client_valid_access_token, db):
    # Create a node threat type
    helpers.create_node_threat_type(value="test_type", db=db)

    # Create the object
    create = client_valid_access_token.post("/api/node/threat/", json={"types": ["test_type"], "value": "test"})
    assert create.status_code == status.HTTP_201_CREATED

    # Read it back
    get = client_valid_access_token.get(create.headers["Content-Location"])
    assert get.json()["value"] == "test"
