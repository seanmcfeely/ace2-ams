from urllib.parse import unquote_plus, urlencode


def test_get_all_event_vectors(client_valid_access_token, requests_mock):
    params = urlencode({"limit": 50, "offset": 0})

    requests_mock.get(
        f"http://db-api/api/event/vector/?{params}", json={"items": [], "total": 0, "limit": 50, "offset": 0}
    )

    client_valid_access_token.get(f"/api/event/vector/?{params}")

    assert (len(requests_mock.request_history)) == 2
    assert requests_mock.request_history[1].method == "GET"
    assert unquote_plus(requests_mock.request_history[1].url) == unquote_plus(
        f"http://db-api/api/event/vector/?{params}"
    )
