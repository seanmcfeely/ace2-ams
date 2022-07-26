import uuid

from fastapi import status

from tests import factory


#
# INVALID TESTS
#


def test_get_invalid_uuid(client):
    get = client.get("/api/analysis/mode/1")
    assert get.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_uuid(client):
    get = client.get(f"/api/analysis/mode/{uuid.uuid4()}")
    assert get.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


def test_get_all(client):
    # conftest creates four default analysis mode objects since they are required to create submissions.

    # Read them back
    get = client.get("/api/analysis/mode/")
    assert get.status_code == status.HTTP_200_OK
    assert get.json()["total"] == 4
