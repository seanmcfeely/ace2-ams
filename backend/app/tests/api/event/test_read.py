import uuid

from datetime import datetime, timedelta
from dateutil.parser import parse
from fastapi import status
from urllib.parse import urlencode

from tests import helpers


#
# INVALID TESTS
#


def test_get_invalid_uuid(client_valid_access_token):
    get = client_valid_access_token.get("/api/event/1")
    assert get.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_uuid(client_valid_access_token):
    get = client_valid_access_token.get(f"/api/event/{uuid.uuid4()}")
    assert get.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


def test_auto_alert_time(client_valid_access_token, db):
    # Create an event
    event = helpers.create_event(name="test event", db=db)

    # The auto_alert_time should be empty
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert get.json()["auto_alert_time"] is None

    # Add an alert to the event
    now = datetime.utcnow()
    alert_tree1 = helpers.create_alert(db=db, event=event, insert_time=now)

    # Verify the auto_alert_time
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert parse(get.json()["auto_alert_time"]).timestamp() == alert_tree1.node.insert_time.timestamp()

    # Add a second alert to the event with an earlier insert time
    earlier = now - timedelta(seconds=5)
    alert_tree2 = helpers.create_alert(db=db, event=event, insert_time=earlier)

    # Verify the new auto_alert_time
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert parse(get.json()["auto_alert_time"]).timestamp() == alert_tree2.node.insert_time.timestamp()


def test_auto_disposition_time(client_valid_access_token, db):
    # Create an event
    event = helpers.create_event(name="test event", db=db)

    # The auto_disposition_time should be empty
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert get.json()["auto_disposition_time"] is None

    # Add an alert to the event
    now = datetime.utcnow()
    alert_tree1 = helpers.create_alert(db=db, event=event, disposition="DELIVERY", update_time=now)

    # Verify the auto_disposition_time
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert parse(get.json()["auto_disposition_time"]) == alert_tree1.node.disposition_time_earliest

    # Add a second alert to the event with an earlier disposition time
    earlier = now - timedelta(seconds=5)
    alert_tree2 = helpers.create_alert(db=db, event=event, disposition="DELIVERY", update_time=earlier)

    # Verify the new auto_disposition_time
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert parse(get.json()["auto_disposition_time"]) == alert_tree2.node.disposition_time_earliest


def test_auto_event_time(client_valid_access_token, db):
    # Create an event
    event = helpers.create_event(name="test event", db=db)

    # The auto_event_time should be empty
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert get.json()["auto_event_time"] is None

    # Add an alert to the event
    now = datetime.utcnow()
    alert_tree1 = helpers.create_alert(db=db, event=event, event_time=now)

    # Verify the auto_event_time
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert parse(get.json()["auto_event_time"]).timestamp() == alert_tree1.node.event_time.timestamp()

    # Add a second alert to the event with an earlier insert time
    earlier = now - timedelta(seconds=5)
    alert_tree2 = helpers.create_alert(db=db, event=event, event_time=earlier)

    # Verify the new auto_event_time
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert parse(get.json()["auto_event_time"]).timestamp() == alert_tree2.node.event_time.timestamp()


def test_auto_ownership_time(client_valid_access_token, db):
    # Create an event
    event = helpers.create_event(name="test event", db=db)

    # The auto_ownership_time should be empty
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert get.json()["auto_ownership_time"] is None

    # Add an alert to the event
    now = datetime.utcnow()
    alert_tree1 = helpers.create_alert(db=db, event=event, owner="alice", update_time=now)

    # Verify the auto_ownership_time
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert parse(get.json()["auto_ownership_time"]) == alert_tree1.node.ownership_time_earliest

    # Add a second alert to the event with an earlier ownership time
    earlier = now - timedelta(seconds=5)
    alert_tree2 = helpers.create_alert(db=db, event=event, owner="alice", update_time=earlier)

    # Verify the new auto_ownership_time
    get = client_valid_access_token.get(f"/api/event/{event.uuid}")
    assert parse(get.json()["auto_ownership_time"]) == alert_tree2.node.ownership_time_earliest


def test_get_all_pagination(client_valid_access_token, db):
    # Create 11 events
    for i in range(11):
        helpers.create_event(name=f"event{i}", db=db)

    # Keep track of all of the event UUIDs to make sure we read them all
    unique_event_uuids = set()

    # Read every page in chunks of 2 while there are still results
    offset = 0
    while True:
        get = client_valid_access_token.get(f"/api/event/?limit=2&offset={offset}")

        # Store the event UUIDs
        for event in get.json()["items"]:
            unique_event_uuids.add(event["uuid"])

            # Make sure the node_type field is "event"
            assert event["node_type"] == "event"

        # Check if there is another page to retrieve
        if len(unique_event_uuids) < get.json()["total"]:
            # Increase the offset to get the next page
            offset += get.json()["limit"]
            continue

        break

    # Should have gotten all 11 events across the pages
    assert len(unique_event_uuids) == 11


def test_get_all_empty(client_valid_access_token):
    get = client_valid_access_token.get("/api/event/")
    assert get.status_code == status.HTTP_200_OK
    assert get.json() == {"items": [], "limit": 50, "offset": 0, "total": 0}


def test_get_filter_alert_time_after(client_valid_access_token, db):
    event1 = helpers.create_event(name="event1", db=db)
    helpers.create_alert(event=event1, insert_time=datetime.utcnow() - timedelta(seconds=5), db=db)

    event2 = helpers.create_event(name="event2", db=db)
    alert_tree2 = helpers.create_alert(event=event2, insert_time=datetime.utcnow(), db=db)

    event3 = helpers.create_event(name="event3", db=db)
    alert_tree3 = helpers.create_alert(event=event3, insert_time=datetime.utcnow() + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by alert_time_after. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"alert_time_after": alert_tree2.node.insert_time}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"
    assert parse(get.json()["items"][0]["auto_alert_time"]) == alert_tree3.node.insert_time


def test_get_filter_alert_time_before(client_valid_access_token, db):
    event1 = helpers.create_event(name="event1", db=db)
    alert_tree1 = helpers.create_alert(event=event1, insert_time=datetime.utcnow() - timedelta(seconds=5), db=db)

    event2 = helpers.create_event(name="event2", db=db)
    alert_tree2 = helpers.create_alert(event=event2, insert_time=datetime.utcnow(), db=db)

    event3 = helpers.create_event(name="event3", db=db)
    helpers.create_alert(event=event3, insert_time=datetime.utcnow() + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by alert_time_after. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"alert_time_before": alert_tree2.node.insert_time}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"
    assert parse(get.json()["items"][0]["auto_alert_time"]) == alert_tree1.node.insert_time


def test_get_filter_contain_time_after(client_valid_access_token, db):
    helpers.create_event(name="event1", contain_time=datetime.utcnow() - timedelta(seconds=5), db=db)
    event2 = helpers.create_event(name="event2", contain_time=datetime.utcnow(), db=db)
    helpers.create_event(name="event3", contain_time=datetime.utcnow() + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by contain_time_after. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"contain_time_after": event2.contain_time}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"


def test_get_filter_contain_time_before(client_valid_access_token, db):
    helpers.create_event(name="event1", contain_time=datetime.utcnow() - timedelta(seconds=5), db=db)
    event2 = helpers.create_event(name="event2", contain_time=datetime.utcnow(), db=db)
    helpers.create_event(name="event3", contain_time=datetime.utcnow() + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by contain_time_before. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"contain_time_before": event2.contain_time}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"


def test_get_filter_created_time_after(client_valid_access_token, db):
    helpers.create_event(name="event1", created_time=datetime.utcnow() - timedelta(seconds=5), db=db)
    event2 = helpers.create_event(name="event2", created_time=datetime.utcnow(), db=db)
    helpers.create_event(name="event3", created_time=datetime.utcnow() + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by created_time_after. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"created_time_after": event2.creation_time}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"


def test_get_filter_created_time_before(client_valid_access_token, db):
    helpers.create_event(name="event1", created_time=datetime.utcnow() - timedelta(seconds=5), db=db)
    event2 = helpers.create_event(name="event2", created_time=datetime.utcnow(), db=db)
    helpers.create_event(name="event3", created_time=datetime.utcnow() + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by created_time_before. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"created_time_before": event2.creation_time}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"


def test_get_filter_disposition(client_valid_access_token, db):
    event1 = helpers.create_event(name="event1", contain_time=datetime.utcnow() - timedelta(seconds=5), db=db)
    helpers.create_alert(event=event1, db=db)

    event2 = helpers.create_event(name="event2", contain_time=datetime.utcnow(), db=db)
    helpers.create_alert(event=event2, db=db, disposition="FALSE_POSITIVE")

    # There should be 2 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 2

    # There should only be 1 event when we filter by the disposition
    get = client_valid_access_token.get("/api/event/?disposition=none")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"

    get = client_valid_access_token.get("/api/event/?disposition=FALSE_POSITIVE")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event2"


def test_get_filter_disposition_time_after(client_valid_access_token, db):
    now = datetime.utcnow()

    event1 = helpers.create_event(name="event1", db=db)
    helpers.create_alert(event=event1, disposition="DELIVERY", update_time=now - timedelta(seconds=5), db=db)

    event2 = helpers.create_event(name="event2", db=db)
    helpers.create_alert(event=event2, disposition="DELIVERY", update_time=now, db=db)

    event3 = helpers.create_event(name="event3", db=db)
    helpers.create_alert(event=event3, disposition="DELIVERY", update_time=now + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by disposition_time_after. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"disposition_time_after": now}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"


def test_get_filter_disposition_time_before(client_valid_access_token, db):
    now = datetime.utcnow()

    event1 = helpers.create_event(name="event1", db=db)
    helpers.create_alert(event=event1, disposition="DELIVERY", update_time=now - timedelta(seconds=5), db=db)

    event2 = helpers.create_event(name="event2", db=db)
    helpers.create_alert(event=event2, disposition="DELIVERY", update_time=now, db=db)

    event3 = helpers.create_event(name="event3", db=db)
    helpers.create_alert(event=event3, disposition="DELIVERY", update_time=now + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by disposition_time_before. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"disposition_time_before": now}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"


def test_get_filter_name(client_valid_access_token, db):
    helpers.create_event(db=db, name="Test Event")
    helpers.create_event(db=db, name="Some Other Event")

    # There should be 2 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 2

    # There should only be 1 event when we filter by the name
    get = client_valid_access_token.get("/api/event/?name=test")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "Test Event"


def test_get_filter_observable(client_valid_access_token, db):
    # Create an empty event
    event1 = helpers.create_event(name="event1", db=db)
    helpers.create_alert(db=db, event=event1)

    # Create some events with one observable
    event2 = helpers.create_event(name="event2", db=db)
    alert_tree2 = helpers.create_alert(db=db, event=event2)
    helpers.create_observable(parent_tree=alert_tree2, type="test_type1", value="test_value1", db=db)

    event3 = helpers.create_event(name="event3", db=db)
    alert_tree3 = helpers.create_alert(db=db, event=event3)
    helpers.create_observable(parent_tree=alert_tree3, type="test_type2", value="test_value2", db=db)

    # Create an event with multiple observables
    event4 = helpers.create_event(name="event4", db=db)
    alert_tree4 = helpers.create_alert(db=db, event=event4)
    helpers.create_observable(parent_tree=alert_tree4, type="test_type1", value="test_value_asdf", db=db)
    helpers.create_observable(parent_tree=alert_tree4, type="test_type2", value="test_value1", db=db)
    helpers.create_observable(parent_tree=alert_tree4, type="test_type2", value="test_value2", db=db)

    # There should be 4 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 4

    # There should only be 1 event when we filter by the test_type1/test_value1 observable
    get = client_valid_access_token.get("/api/event/?observable=test_type1|test_value1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event2"

    # There should be 2 events when we filter by the test_type2/test_value2 observable
    get = client_valid_access_token.get("/api/event/?observable=test_type2|test_value2")
    assert get.json()["total"] == 2
    assert any(a["name"] == "event3" for a in get.json()["items"])
    assert any(a["name"] == "event4" for a in get.json()["items"])


def test_get_filter_observable_types(client_valid_access_token, db):
    # Create an empty event
    event1 = helpers.create_event(name="event1", db=db)
    helpers.create_alert(db=db, event=event1)

    # Create an event with one observable
    event2 = helpers.create_event(name="event2", db=db)
    alert_tree2 = helpers.create_alert(db=db, event=event2)
    helpers.create_observable(parent_tree=alert_tree2, type="test_type1", value="test_value1", db=db)

    # Create an alert with multiple observables
    event3 = helpers.create_event(name="event3", db=db)
    alert_tree3 = helpers.create_alert(db=db, event=event3)
    helpers.create_observable(parent_tree=alert_tree3, type="test_type1", value="test_value_asdf", db=db)
    helpers.create_observable(parent_tree=alert_tree3, type="test_type2", value="test_value1", db=db)
    helpers.create_observable(parent_tree=alert_tree3, type="test_type2", value="test_value2", db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should be 2 events when we filter by just test_type1
    get = client_valid_access_token.get("/api/event/?observable_types=test_type1")
    assert get.json()["total"] == 2
    assert any(a["name"] == "event2" for a in get.json()["items"])
    assert any(a["name"] == "event3" for a in get.json()["items"])

    # There should only be 1 event when we filter by the test_type1 and test_type2
    get = client_valid_access_token.get("/api/event/?observable_types=test_type1,test_type2")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"


def test_get_filter_observable_value(client_valid_access_token, db):
    # Create an empty event
    event1 = helpers.create_event(name="event1", db=db)
    helpers.create_alert(db=db, event=event1)

    # Create some alerts with one observable
    event2 = helpers.create_event(name="event2", db=db)
    alert_tree2 = helpers.create_alert(db=db, event=event2)
    helpers.create_observable(parent_tree=alert_tree2, type="test_type1", value="test_value1", db=db)

    event3 = helpers.create_event(name="event3", db=db)
    alert_tree3 = helpers.create_alert(db=db, event=event3)
    helpers.create_observable(parent_tree=alert_tree3, type="test_type2", value="test_value2", db=db)

    # Create an event with multiple observables
    event4 = helpers.create_event(name="event4", db=db)
    alert_tree4 = helpers.create_alert(db=db, event=event4)
    helpers.create_observable(parent_tree=alert_tree4, type="test_type1", value="test_value_asdf", db=db)
    helpers.create_observable(parent_tree=alert_tree4, type="test_type2", value="test_value1", db=db)
    helpers.create_observable(parent_tree=alert_tree4, type="test_type2", value="test_value2", db=db)

    # There should be 4 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 4

    # There should only be 1 event when we filter by the test_value_asdf observable value
    get = client_valid_access_token.get("/api/event/?observable_value=test_value_asdf")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event4"

    # There should be 2 events when we filter by the test_value1 observable value
    get = client_valid_access_token.get("/api/event/?observable_value=test_value1")
    assert get.json()["total"] == 2
    assert any(a["name"] == "event2" for a in get.json()["items"])
    assert any(a["name"] == "event4" for a in get.json()["items"])


def test_get_filter_owner(client_valid_access_token, db):
    helpers.create_user(username="analyst", db=db)
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db, owner="analyst")

    # There should be 2 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 2

    # There should only be 1 event when we filter by the owner
    get = client_valid_access_token.get("/api/event/?owner=analyst")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["owner"]["username"] == "analyst"


def test_get_filter_prevention_tools(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db, prevention_tools=["value1"])
    helpers.create_event(name="event3", db=db, prevention_tools=["value2", "value3"])

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by value1
    get = client_valid_access_token.get("/api/event/?prevention_tools=value1")
    assert get.json()["total"] == 1
    assert len(get.json()["items"][0]["prevention_tools"]) == 1
    assert get.json()["items"][0]["prevention_tools"][0]["value"] == "value1"

    # There should only be 1 event when we filter by value2 AND value3
    get = client_valid_access_token.get("/api/event/?prevention_tools=value2,value3")
    assert get.json()["total"] == 1
    assert len(get.json()["items"][0]["prevention_tools"]) == 2
    assert any(t["value"] == "value2" for t in get.json()["items"][0]["prevention_tools"])
    assert any(t["value"] == "value3" for t in get.json()["items"][0]["prevention_tools"])

    # All the events should be returned if you don't specify any value for the filter
    get = client_valid_access_token.get("/api/event/?prevention_tools=")
    assert get.json()["total"] == 3


def test_get_filter_queue(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db, queue="test_queue1")
    helpers.create_event(name="event2", db=db, queue="test_queue2")

    # There should be 2 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 2

    # There should only be 1 event when we filter by the queue
    get = client_valid_access_token.get("/api/event/?queue=test_queue1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["queue"]["value"] == "test_queue1"


def test_get_filter_remediation_time_after(client_valid_access_token, db):
    helpers.create_event(name="event1", remediation_time=datetime.utcnow() - timedelta(seconds=5), db=db)
    event2 = helpers.create_event(name="event2", remediation_time=datetime.utcnow(), db=db)
    helpers.create_event(name="event3", remediation_time=datetime.utcnow() + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by remediation_time_after. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"remediation_time_after": event2.remediation_time}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"


def test_get_filter_remediation_time_before(client_valid_access_token, db):
    helpers.create_event(name="event1", remediation_time=datetime.utcnow() - timedelta(seconds=5), db=db)
    event2 = helpers.create_event(name="event2", remediation_time=datetime.utcnow(), db=db)
    helpers.create_event(name="event3", remediation_time=datetime.utcnow() + timedelta(seconds=5), db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by remediation_time_before. But the timestamp
    # has a timezone specified, which uses the + symbol that needs to be urlencoded since it
    # is a reserved URL character.
    params = {"remediation_time_before": event2.remediation_time}
    get = client_valid_access_token.get(f"/api/event/?{urlencode(params)}")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"


def test_get_filter_remediations(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db, remediations=["value1"])
    helpers.create_event(name="event3", db=db, remediations=["value2", "value3"])

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by value1
    get = client_valid_access_token.get("/api/event/?remediations=value1")
    assert get.json()["total"] == 1
    assert len(get.json()["items"][0]["remediations"]) == 1
    assert get.json()["items"][0]["remediations"][0]["value"] == "value1"

    # There should only be 1 event when we filter by value2 AND value3
    get = client_valid_access_token.get("/api/event/?remediations=value2,value3")
    assert get.json()["total"] == 1
    assert len(get.json()["items"][0]["remediations"]) == 2
    assert any(t["value"] == "value2" for t in get.json()["items"][0]["remediations"])
    assert any(t["value"] == "value3" for t in get.json()["items"][0]["remediations"])

    # All the events should be returned if you don't specify any value for the filter
    get = client_valid_access_token.get("/api/event/?remediations=")
    assert get.json()["total"] == 3


def test_get_filter_risk_level(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db, risk_level="value1")

    # There should be 2 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 2

    # There should only be 1 event when we filter by value1
    get = client_valid_access_token.get("/api/event/?risk_level=value1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["risk_level"]["value"] == "value1"

    # All the events should be returned if you don't specify any value for the filter
    get = client_valid_access_token.get("/api/event/?risk_level=")
    assert get.json()["total"] == 2


def test_get_filter_source(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db, source="value1")

    # There should be 2 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 2

    # There should only be 1 event when we filter by value1
    get = client_valid_access_token.get("/api/event/?source=value1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["source"]["value"] == "value1"

    # All the events should be returned if you don't specify any value for the filter
    get = client_valid_access_token.get("/api/event/?source=")
    assert get.json()["total"] == 2


def test_get_filter_status(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db, status="value1")
    helpers.create_event(name="event2", db=db, status="value2")

    # There should be 2 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 2

    # There should only be 1 event when we filter by value1
    get = client_valid_access_token.get("/api/event/?status=value1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["status"]["value"] == "value1"

    # All the events should be returned if you don't specify any value for the filter
    get = client_valid_access_token.get("/api/event/?status=")
    assert get.json()["total"] == 2


def test_get_filter_tags(client_valid_access_token, db):
    # Create an event with a tagged observable
    event1 = helpers.create_event(name="event1", db=db)
    alert_tree1 = helpers.create_alert(event=event1, db=db)
    helpers.create_observable(type="fqdn", value="bad.com", parent_tree=alert_tree1, db=db, tags=["obs1"])

    # Create an event with an alert with one tag
    event2 = helpers.create_event(name="event2", db=db)
    helpers.create_alert(event=event2, db=db, tags=["tag1"])

    # Create an event with an alert with two tags
    event3 = helpers.create_event(name="event3", db=db)
    helpers.create_alert(event=event3, db=db, tags=["tag2", "tag3"])

    # Create a tagged event
    event4 = helpers.create_event(name="event4", db=db, tags=["tag4"])
    helpers.create_alert(event=event4, db=db)

    # There should be 4 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 4

    # There should only be 1 event when we filter by tag1
    get = client_valid_access_token.get("/api/event/?tags=tag1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event2"

    # There should only be 1 event when we filter by tag2 AND tag3
    get = client_valid_access_token.get("/api/event/?tags=tag2,tag3")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"

    # There should only be 1 event when we filter by the child observable tag obs1
    get = client_valid_access_token.get("/api/event/?tags=obs1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"

    # There should only be 1 event when we filter by tag4
    get = client_valid_access_token.get("/api/event/?tags=tag4")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event4"

    # All the events should be returned if you don't specify any tags for the filter
    get = client_valid_access_token.get("/api/event/?tags=")
    assert get.json()["total"] == 4


def test_get_filter_threat_actors(client_valid_access_token, db):
    event1 = helpers.create_event(name="event1", db=db)
    alert_tree1 = helpers.create_alert(event=event1, db=db)
    helpers.create_observable(type="fqdn", value="bad.com", parent_tree=alert_tree1, db=db, threat_actors=["bad_guys"])

    event2 = helpers.create_event(name="event2", db=db)
    helpers.create_alert(event=event2, db=db, threat_actors=["test_actor"])

    event3 = helpers.create_event(name="event3", db=db, threat_actors=["test_actor2"])
    helpers.create_alert(event=event3, db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should be 1 event when we filter test_actor
    get = client_valid_access_token.get("/api/event/?threat_actors=test_actor")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event2"

    # There should be 1 event when we filter by the child observable threat_actor
    get = client_valid_access_token.get("/api/event/?threat_actors=bad_guys")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"

    # There should be 1 event when we filter test_actor2
    get = client_valid_access_token.get("/api/event/?threat_actors=test_actor2")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"

    # All the alerts should be returned if you don't specify anything for the filter
    get = client_valid_access_token.get("/api/event/?threat_actors=")
    assert get.json()["total"] == 3


def test_get_filter_threats(client_valid_access_token, db):
    event1 = helpers.create_event(name="event1", db=db)
    alert_tree1 = helpers.create_alert(event=event1, db=db)
    helpers.create_observable(type="fqdn", value="bad.com", parent_tree=alert_tree1, db=db, threats=["malz"])

    event2 = helpers.create_event(name="event2", db=db)
    helpers.create_alert(event=event2, db=db, threats=["threat1"])

    event3 = helpers.create_event(name="event3", db=db, threats=["threat2", "threat3"])
    helpers.create_alert(event=event3, db=db)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should be 1 event when we filter by threat1
    get = client_valid_access_token.get("/api/event/?threats=threat1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event2"

    # There should be 1 event when we filter by the child observable threat
    get = client_valid_access_token.get("/api/event/?threats=malz")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event1"

    # There should be 1 event when we filter by threat2 AND threat3
    get = client_valid_access_token.get("/api/event/?threats=threat2,threat3")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event3"

    # All the alerts should be returned if you don't specify anything for the filter
    get = client_valid_access_token.get("/api/event/?threats=")
    assert get.json()["total"] == 3


def test_get_filter_type(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db, type="test_type")
    helpers.create_event(name="event2", db=db, type="test_type2")

    # There should be 2 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 2

    # There should only be 1 event when we filter by test_type
    get = client_valid_access_token.get("/api/event/?type=test_type")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["type"]["value"] == "test_type"


def test_get_filter_vectors(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db, vectors=["value1"])
    helpers.create_event(name="event3", db=db, vectors=["value2", "value3"])

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by value1
    get = client_valid_access_token.get("/api/event/?vectors=value1")
    assert get.json()["total"] == 1
    assert len(get.json()["items"][0]["vectors"]) == 1
    assert get.json()["items"][0]["vectors"][0]["value"] == "value1"

    # There should only be 1 event when we filter by value2 AND value3
    get = client_valid_access_token.get("/api/event/?vectors=value2,value3")
    assert get.json()["total"] == 1
    assert len(get.json()["items"][0]["vectors"]) == 2
    assert any(t["value"] == "value2" for t in get.json()["items"][0]["vectors"])
    assert any(t["value"] == "value3" for t in get.json()["items"][0]["vectors"])

    # All the events should be returned if you don't specify any value for the filter
    get = client_valid_access_token.get("/api/event/?vectors=")
    assert get.json()["total"] == 3


def test_get_multiple_filters(client_valid_access_token, db):
    event1 = helpers.create_event(name="event1", db=db, type="test_type1")
    helpers.create_alert(db=db, event=event1)

    event2 = helpers.create_event(name="event2", db=db, type="test_type1", prevention_tools=["tool1"])
    helpers.create_alert(db=db, event=event2)

    event2 = helpers.create_event(name="event2", db=db, type="test_type2")
    helpers.create_alert(db=db, event=event2)

    # There should be 3 total events
    get = client_valid_access_token.get("/api/event/")
    assert get.json()["total"] == 3

    # There should only be 1 event when we filter by the type and prevention_tools
    get = client_valid_access_token.get("/api/event/?type=test_type1&prevention_tools=tool1")
    assert get.json()["total"] == 1
    assert get.json()["items"][0]["name"] == "event2"


def test_get_sort_by_created_time(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db, created_time=datetime.utcnow())
    helpers.create_event(name="event2", db=db, created_time=datetime.utcnow() + timedelta(seconds=5))

    # If you sort descending, the newest event (event2) should appear first
    get = client_valid_access_token.get("/api/event/?sort=created_time|desc")
    assert get.json()["total"] == 2
    assert get.json()["items"][0]["name"] == "event2"
    assert get.json()["items"][1]["name"] == "event1"

    # If you sort ascending, the oldest event (event1) should appear first
    get = client_valid_access_token.get("/api/event/?sort=created_time|asc")
    assert get.json()["total"] == 2
    assert get.json()["items"][0]["name"] == "event1"
    assert get.json()["items"][1]["name"] == "event2"


def test_get_sort_by_name(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db)

    # If you sort descending: event2, event1
    get = client_valid_access_token.get("/api/event/?sort=name|desc")
    assert get.json()["total"] == 2
    assert get.json()["items"][0]["name"] == "event2"
    assert get.json()["items"][1]["name"] == "event1"

    # If you sort ascending: event1, event2
    get = client_valid_access_token.get("/api/event/?sort=name|asc")
    assert get.json()["total"] == 2
    assert get.json()["items"][0]["name"] == "event1"
    assert get.json()["items"][1]["name"] == "event2"


def test_get_sort_by_owner(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db, owner="alice")
    helpers.create_event(name="event2", db=db, owner="bob")

    # If you sort descending: event2, event1
    get = client_valid_access_token.get("/api/event/?sort=owner|desc")
    assert get.json()["total"] == 2
    assert get.json()["items"][0]["name"] == "event2"
    assert get.json()["items"][1]["name"] == "event1"

    # If you sort ascending: event1, event2
    get = client_valid_access_token.get("/api/event/?sort=owner|asc")
    assert get.json()["total"] == 2
    assert get.json()["items"][0]["name"] == "event1"
    assert get.json()["items"][1]["name"] == "event2"


def test_get_sort_by_risk_level(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db, risk_level="value1")
    helpers.create_event(name="event3", db=db, risk_level="value2")

    # If you sort descending: event1, event3, event2
    get = client_valid_access_token.get("/api/event/?sort=risk_level|desc")
    assert get.json()["total"] == 3
    assert get.json()["items"][0]["name"] == "event1"
    assert get.json()["items"][1]["name"] == "event3"
    assert get.json()["items"][2]["name"] == "event2"

    # If you sort ascending: event2, event3, event1
    get = client_valid_access_token.get("/api/event/?sort=risk_level|asc")
    assert get.json()["total"] == 3
    assert get.json()["items"][0]["name"] == "event2"
    assert get.json()["items"][1]["name"] == "event3"
    assert get.json()["items"][2]["name"] == "event1"


def test_get_sort_by_status(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db, status="value1")
    helpers.create_event(name="event2", db=db, status="value2")

    # If you sort descending: event2, event1
    get = client_valid_access_token.get("/api/event/?sort=status|desc")
    assert get.json()["total"] == 2
    assert get.json()["items"][0]["name"] == "event2"
    assert get.json()["items"][1]["name"] == "event1"

    # If you sort ascending: event1, event2
    get = client_valid_access_token.get("/api/event/?sort=status|asc")
    assert get.json()["total"] == 2
    assert get.json()["items"][0]["name"] == "event1"
    assert get.json()["items"][1]["name"] == "event2"


def test_get_sort_by_type(client_valid_access_token, db):
    helpers.create_event(name="event1", db=db)
    helpers.create_event(name="event2", db=db, type="value1")
    helpers.create_event(name="event3", db=db, type="value2")

    # If you sort descending: event1, event3, event2
    get = client_valid_access_token.get("/api/event/?sort=type|desc")
    assert get.json()["total"] == 3
    assert get.json()["items"][0]["name"] == "event1"
    assert get.json()["items"][1]["name"] == "event3"
    assert get.json()["items"][2]["name"] == "event2"

    # If you sort ascending: event2, event3, event1
    get = client_valid_access_token.get("/api/event/?sort=type|asc")
    assert get.json()["total"] == 3
    assert get.json()["items"][0]["name"] == "event2"
    assert get.json()["items"][1]["name"] == "event3"
    assert get.json()["items"][2]["name"] == "event1"
