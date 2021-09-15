import pytest
import time

from fastapi import status

from core.config import Settings
from tests.helpers import create_test_user
from main import app


#
# INVALID TESTS


@pytest.mark.parametrize(
    "username,password",
    [
        ("johndoe", "wrongpassword"),
        ("wronguser", "abcd1234"),
    ],
)
def test_auth_invalid(client, db, username, password):
    create_test_user(db, "johndoe", "abcd1234")

    # Attempt to authenticate
    auth = client.post("/api/auth/", data={"username": username, "password": password})
    assert auth.status_code == status.HTTP_401_UNAUTHORIZED

    # Attempt to use a bogus token to access a protected API endpoint
    get = client.get("/api/user/", headers={"Authorization": "Bearer asdf"})
    assert get.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_token(client, db, monkeypatch):
    def mock_get_settings():
        settings = Settings()
        settings.jwt_expire_seconds = 1
        return settings

    # Patching __code__ works no matter how the function is imported
    monkeypatch.setattr("core.config.get_settings.__code__", mock_get_settings.__code__)

    create_test_user(db, "johndoe", "abcd1234")

    # Attempt to authenticate
    auth = client.post("/api/auth/", data={"username": "johndoe", "password": "abcd1234"})
    token = auth.json()["access_token"]
    assert auth.status_code == status.HTTP_200_OK
    assert auth.json()["token_type"] == "bearer"
    assert token

    # Attempt to use the token to access a protected API endpoint
    get = client.get("/api/user/", headers={"Authorization": f"Bearer {token}"})
    assert get.status_code == status.HTTP_200_OK
    assert len(get.json()) == 1

    # Wait for the token to expire
    time.sleep(2)

    # Attempt to use the token to access a protected API endpoint now that the token is expired
    get = client.get("/api/user/", headers={"Authorization": f"Bearer {token}"})
    assert get.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "route",
    [
        route for route in app.routes if route.path.startswith("/api/")
    ],
)
def test_invalid_token(client, route):
    """
    This tests every registered API endpoint to ensure that it requires token authentication.
    """

    # There are some special endpoints that do not require authentication.
    if route.path in ["/api/ping", "/api/auth/"]:
        return

    for method in route.methods:
        if method == "POST":
            client_method = client.post
        elif method == "GET":
            client_method = client.get
        elif method == "PATCH":
            client_method = client.patch
        elif method == "DELETE":
            client_method = client.delete
        else:
            raise ValueError(f"Test does not account for method: {method}")

        result = client_method(route.path)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED, f"{method} on {route.path} does not require auth!"


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


#
# VALID TESTS
#


def test_auth_success(client, db):
    create_test_user(db, "johndoe", "abcd1234")

    # Attempt to authenticate
    auth = client.post("/api/auth/", data={"username": "johndoe", "password": "abcd1234"})
    token = auth.json()["access_token"]
    assert auth.status_code == status.HTTP_200_OK
    assert auth.json()["token_type"] == "bearer"
    assert token

    # Attempt to use the token to access a protected API endpoint
    get = client.get("/api/user/", headers={"Authorization": f"Bearer {token}"})
    assert get.status_code == status.HTTP_200_OK
    assert len(get.json()) == 1
