from fastapi import status
from uuid import uuid4


def test_update_node_comment(client_valid_access_token, requests_mock):
    node_comment_uuid = str(uuid4())

    requests_mock.patch(
        f"http://db-api/api/node/comment/{node_comment_uuid}?history_username=analyst",
        status_code=status.HTTP_204_NO_CONTENT,
    )

    client_valid_access_token.patch(
        f"/api/node/comment/{node_comment_uuid}", json={"username": "analyst", "value": "value"}
    )

    assert (len(requests_mock.request_history)) == 2
    assert requests_mock.request_history[1].method == "PATCH"
    assert (
        requests_mock.request_history[1].url
        == f"http://db-api/api/node/comment/{node_comment_uuid}?history_username=analyst"
    )
