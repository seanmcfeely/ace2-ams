import pytest

from fastapi import status


@pytest.mark.parametrize(
    "username,password,expected_status_code",
    [
        ("johndoe", "abcd1234", status.HTTP_200_OK),
        ("johndoe", "wrongpassword", status.HTTP_401_UNAUTHORIZED),
        ("wronguser", "abcd1234", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_auth(client, username, password, expected_status_code):
    # Create an alert queue
    client.post("/api/alert/queue/", json={"value": "test_queue"})

    # Create a user role
    client.post("/api/user/role/", json={"value": "test_role"})

    # Create a user
    create_json = {
        "default_alert_queue": "test_queue",
        "display_name": "John Doe",
        "email": "john@test.com",
        "password": "abcd1234",
        "roles": ["test_role"],
        "username": "johndoe",
    }
    create = client.post("/api/user/", json=create_json)
    assert create.status_code == status.HTTP_201_CREATED

    # Attempt to authenticate
    auth = client.post("/api/auth/", json={"username": username, "password": password})
    assert auth.status_code == expected_status_code


@pytest.mark.parametrize(
    "key",
    [
        ("username"),
        ("password"),
    ],
)
def test_missing_required_fields(client, key):
    create_json = {"username": "johndoe", "password": "abcd1234"}
    del create_json[key]
    create = client.post("/api/auth/", json=create_json)
    assert create.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
