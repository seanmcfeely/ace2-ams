import uuid

from fastapi import status

from tests import helpers


#
# INVALID TESTS
#


def test_get_invalid_uuid(client_valid_access_token):
    get = client_valid_access_token.get("/api/observable/1")
    assert get.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_uuid(client_valid_access_token):
    get = client_valid_access_token.get(f"/api/observable/{uuid.uuid4()}")
    assert get.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


def test_get(client_valid_access_token, db):
    alert_tree = helpers.create_alert(db=db)
    observable_tree = helpers.create_observable(type="test_type", value="test_value", parent_tree=alert_tree, db=db)

    get = client_valid_access_token.get(f"/api/observable/{observable_tree.node.uuid}")
    assert get.status_code == status.HTTP_200_OK
    assert get.json()["node_type"] == "observable"


def test_get_all(client_valid_access_token, db):
    alert_tree = helpers.create_alert(db=db)
    observable_tree = helpers.create_observable(type="test_type", value="test", parent_tree=alert_tree, db=db)
    helpers.create_observable(type="test_type", value="test2", parent_tree=alert_tree, db=db)

    # Adding a third observable somewhere in the alert tree with the same type+value combination is allowed,
    # but it will not result in a third entry in the observable table.
    helpers.create_observable(type="test_type", value="test2", parent_tree=observable_tree, db=db)

    # Read them back
    get = client_valid_access_token.get("/api/observable/")
    assert get.status_code == status.HTTP_200_OK
    assert get.json()["total"] == 2


def test_get_all_empty(client_valid_access_token):
    get = client_valid_access_token.get("/api/observable/")
    assert get.status_code == status.HTTP_200_OK
    assert get.json()["total"] == 0