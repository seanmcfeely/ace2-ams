import uuid

from fastapi import status

from db.tests import factory


#
# INVALID TESTS
#


def test_get_invalid_uuid(client):
    get = client.get("/api/user/role/1")
    assert get.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_uuid(client):
    get = client.get(f"/api/user/role/{uuid.uuid4()}")
    assert get.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


def test_get_all(client, db):
    # Create some objects
    factory.user_role.create_or_read(value="test", db=db)
    factory.user_role.create_or_read(value="test2", db=db)

    # Read them back
    get = client.get("/api/user/role/")
    assert get.status_code == status.HTTP_200_OK
    assert get.json()["total"] == 3  # The default user has a role
