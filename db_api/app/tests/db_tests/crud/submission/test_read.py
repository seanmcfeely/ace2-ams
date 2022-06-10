from datetime import timedelta

from api_models.observable import ObservableCreateInSubmission
from api_models.submission import SubmissionUpdate
from db import crud
from tests import factory


def test_filter_by_alert(db):
    submission1 = factory.submission.create(alert=True, db=db)
    factory.submission.create(alert=False, db=db)

    result = crud.submission.read_all(alert=True, db=db)
    assert result == [submission1]


def test_filter_by_disposition(db):
    submission1 = factory.submission.create(disposition="DELIVERY", db=db)
    submission2 = factory.submission.create(db=db)

    result = crud.submission.read_all(disposition="DELIVERY", db=db)
    assert result == [submission1]

    result = crud.submission.read_all(disposition="none", db=db)
    assert result == [submission2]


def test_filter_by_disposition_user(db):
    submission1 = factory.submission.create(
        disposition="DELIVERY",
        updated_by_user="analyst",
        history_username="analyst",
        db=db,
    )
    factory.submission.create(db=db)

    result = crud.submission.read_all(disposition_user="analyst", db=db)
    assert result == [submission1]

    # Another analyst dispositions the same alert
    factory.alert_disposition.create_or_read(value="FALSE_POSITIVE", rank=2, db=db)
    factory.user.create_or_read(username="analyst2", db=db)
    crud.submission.update(
        model=SubmissionUpdate(disposition="FALSE_POSITIVE", history_username="analyst2", uuid=submission1.uuid), db=db
    )

    # The submission should still be returned when filtering by analyst since it uses the submission's history
    assert submission1.disposition_user.username == "analyst2"
    result = crud.submission.read_all(disposition_user="analyst", db=db)
    assert result == [submission1]


def test_filter_by_dispositioned_after(db):
    now = crud.helpers.utcnow()

    factory.submission.create(
        disposition="DELIVERY",
        updated_by_user="analyst",
        update_time=now - timedelta(seconds=5),
        history_username="analyst",
        db=db,
    )
    factory.submission.create(
        disposition="DELIVERY", updated_by_user="analyst", update_time=now, history_username="analyst", db=db
    )
    submission3 = factory.submission.create(
        disposition="DELIVERY",
        updated_by_user="analyst",
        update_time=now + timedelta(seconds=5),
        history_username="analyst",
        db=db,
    )

    result = crud.submission.read_all(dispositioned_after=now, db=db)
    assert result == [submission3]


def test_filter_by_dispositioned_before(db):
    now = crud.helpers.utcnow()

    submission1 = factory.submission.create(
        disposition="DELIVERY",
        updated_by_user="analyst",
        update_time=now - timedelta(seconds=5),
        history_username="analyst",
        db=db,
    )
    factory.submission.create(
        disposition="DELIVERY", updated_by_user="analyst", update_time=now, history_username="analyst", db=db
    )
    factory.submission.create(
        disposition="DELIVERY",
        updated_by_user="analyst",
        update_time=now + timedelta(seconds=5),
        history_username="analyst",
        db=db,
    )

    result = crud.submission.read_all(dispositioned_before=now, db=db)
    assert result == [submission1]


def test_filter_by_event_time_after(db):
    now = crud.helpers.utcnow()

    factory.submission.create(event_time=now - timedelta(seconds=5), db=db)
    factory.submission.create(event_time=now, db=db)
    submission3 = factory.submission.create(event_time=now + timedelta(seconds=5), db=db)

    result = crud.submission.read_all(event_time_after=now, db=db)
    assert result == [submission3]


def test_filter_by_event_time_before(db):
    now = crud.helpers.utcnow()

    submission1 = factory.submission.create(event_time=now - timedelta(seconds=5), db=db)
    factory.submission.create(event_time=now, db=db)
    factory.submission.create(event_time=now + timedelta(seconds=5), db=db)

    result = crud.submission.read_all(event_time_before=now, db=db)
    assert result == [submission1]


def test_filter_by_event_uuid(db):
    event = factory.event.create_or_read(name="test", db=db)
    submission1 = factory.submission.create(event=event, db=db)
    factory.submission.create(db=db)

    result = crud.submission.read_all(event_uuid=event.uuid, db=db)
    assert result == [submission1]


def test_filter_by_insert_time_after(db):
    now = crud.helpers.utcnow()

    factory.submission.create(insert_time=now - timedelta(seconds=5), db=db)
    factory.submission.create(insert_time=now, db=db)
    submission3 = factory.submission.create(insert_time=now + timedelta(seconds=5), db=db)

    result = crud.submission.read_all(insert_time_after=now, db=db)
    assert result == [submission3]


def test_filter_by_insert_time_before(db):
    now = crud.helpers.utcnow()

    submission1 = factory.submission.create(insert_time=now - timedelta(seconds=5), db=db)
    factory.submission.create(insert_time=now, db=db)
    factory.submission.create(insert_time=now + timedelta(seconds=5), db=db)

    result = crud.submission.read_all(insert_time_before=now, db=db)
    assert result == [submission1]


def test_filter_by_name(db):
    submission1 = factory.submission.create(name="submission1", db=db)
    submission2 = factory.submission.create(name="submission2", db=db)

    result = crud.submission.read_all(name="submission1", db=db)
    assert result == [submission1]

    result = crud.submission.read_all(name="submission", db=db)
    assert result == [submission1, submission2]


def test_filter_by_observable(db):
    factory.observable_type.create_or_read(value="type", db=db)

    submission1 = factory.submission.create(
        observables=[ObservableCreateInSubmission(type="type", value="value")], db=db
    )

    factory.submission.create(observables=[ObservableCreateInSubmission(type="type", value="value2")], db=db)

    result = crud.submission.read_all(observable="type|value", db=db)
    assert result == [submission1]


def test_filter_by_observable_types(db):
    factory.observable_type.create_or_read(value="type", db=db)
    factory.observable_type.create_or_read(value="type2", db=db)

    submission1 = factory.submission.create(
        observables=[ObservableCreateInSubmission(type="type", value="value")], db=db
    )

    factory.submission.create(observables=[ObservableCreateInSubmission(type="type2", value="value2")], db=db)

    result = crud.submission.read_all(observable_types="type", db=db)
    assert result == [submission1]


def test_filter_by_observable_value(db):
    factory.observable_type.create_or_read(value="type", db=db)

    submission1 = factory.submission.create(
        observables=[ObservableCreateInSubmission(type="type", value="value")], db=db
    )

    factory.submission.create(observables=[ObservableCreateInSubmission(type="type", value="value2")], db=db)

    result = crud.submission.read_all(observable_value="value", db=db)
    assert result == [submission1]


def test_filter_by_owner(db):
    submission1 = factory.submission.create(owner="analyst", db=db)
    factory.submission.create(db=db)

    result = crud.submission.read_all(owner="analyst", db=db)
    assert result == [submission1]


def test_filter_by_queue(db):
    submission1 = factory.submission.create(alert_queue="queue1", db=db)
    factory.submission.create(alert_queue="queue2", db=db)

    result = crud.submission.read_all(queue="queue1", db=db)
    assert result == [submission1]


def test_filter_by_tags(db):
    submission1 = factory.submission.create(db=db)
    factory.observable.create_or_read(type="type1", value="value1", parent_analysis=submission1.root_analysis, db=db)

    submission2 = factory.submission.create(tags=["submission2_tag"], db=db)
    factory.observable.create_or_read(type="type2", value="value2", parent_analysis=submission2.root_analysis, db=db)

    submission3 = factory.submission.create(db=db)
    factory.observable.create_or_read(
        type="type3",
        value="value3",
        parent_analysis=submission3.root_analysis,
        analysis_tags=["observable3_analysis_tag"],
        db=db,
    )

    submission4 = factory.submission.create(db=db)
    factory.observable.create_or_read(
        type="type4",
        value="value4",
        parent_analysis=submission4.root_analysis,
        permanent_tags=["observable4_permanent_tag"],
        db=db,
    )

    submission5 = factory.submission.create(tags=["submission5_tag"], db=db)
    factory.observable.create_or_read(
        type="type5",
        value="value5",
        parent_analysis=submission5.root_analysis,
        analysis_tags=["observable5_analysis_tag"],
        permanent_tags=["observable5_permanent_tag"],
        db=db,
    )

    assert crud.submission.read_all(tags="submission2_tag", db=db) == [submission2]
    assert crud.submission.read_all(tags="observable3_analysis_tag", db=db) == [submission3]
    assert crud.submission.read_all(tags="observable4_permanent_tag", db=db) == [submission4]
    assert crud.submission.read_all(
        tags="submission5_tag,observable5_analysis_tag,observable5_permanent_tag", db=db
    ) == [submission5]


def test_filter_by_threat_actors(db):
    submission1 = factory.submission.create(db=db)
    factory.observable.create_or_read(type="type1", value="value1", parent_analysis=submission1.root_analysis, db=db)

    submission2 = factory.submission.create(threat_actors=["submission2_actor"], db=db)
    factory.observable.create_or_read(type="type2", value="value2", parent_analysis=submission2.root_analysis, db=db)

    submission3 = factory.submission.create(db=db)
    factory.observable.create_or_read(
        type="type3",
        value="value3",
        parent_analysis=submission3.root_analysis,
        threat_actors=["observable3_actor"],
        db=db,
    )

    result = crud.submission.read_all(threat_actors="submission2_actor", db=db)
    assert result == [submission2]

    result = crud.submission.read_all(threat_actors="observable3_actor", db=db)
    assert result == [submission3]


def test_filter_by_threats(db):
    submission1 = factory.submission.create(db=db)
    factory.observable.create_or_read(type="type1", value="value1", parent_analysis=submission1.root_analysis, db=db)

    submission2 = factory.submission.create(threats=["submission2_actor"], db=db)
    factory.observable.create_or_read(type="type2", value="value2", parent_analysis=submission2.root_analysis, db=db)

    submission3 = factory.submission.create(db=db)
    factory.observable.create_or_read(
        type="type3", value="value3", parent_analysis=submission3.root_analysis, threats=["observable3_actor"], db=db
    )

    result = crud.submission.read_all(threats="submission2_actor", db=db)
    assert result == [submission2]

    result = crud.submission.read_all(threats="observable3_actor", db=db)
    assert result == [submission3]


def test_filter_by_tool(db):
    submission1 = factory.submission.create(tool="tool1", db=db)
    factory.submission.create(tool="tool2", db=db)

    result = crud.submission.read_all(tool="tool1", db=db)
    assert result == [submission1]


def test_filter_by_tool_instance(db):
    submission1 = factory.submission.create(tool_instance="tool_instance1", db=db)
    factory.submission.create(tool_instance="tool_instance2", db=db)

    result = crud.submission.read_all(tool_instance="tool_instance1", db=db)
    assert result == [submission1]


def test_filter_by_type(db):
    submission1 = factory.submission.create(submission_type="type1", db=db)
    factory.submission.create(submission_type="type2", db=db)

    result = crud.submission.read_all(submission_type="type1", db=db)
    assert result == [submission1]


def test_read_all_history(db):
    submission = factory.submission.create(history_username="analyst", db=db)
    result = crud.submission.read_all_history(uuid=submission.uuid, db=db)
    assert len(result) == 1
    assert result[0].action == "CREATE"


def test_read_observables(db):
    # Create a submission tree where the same observable type+value appears twice
    #
    # submission
    #   o1
    #     a
    #       o1
    #   o2
    submission = factory.submission.create(db=db)
    observable1 = factory.observable.create_or_read(
        type="fqdn", value="bad.com", parent_analysis=submission.root_analysis, db=db
    )
    analysis_module_type = factory.analysis_module_type.create_or_read(value="test", db=db)
    analysis = factory.analysis.create_or_read(
        analysis_module_type=analysis_module_type, submission=submission, target=observable1, db=db
    )
    factory.observable.create_or_read(type="fqdn", value="bad.com", parent_analysis=analysis, db=db)
    factory.observable.create_or_read(type="ipv4", value="127.0.0.1", parent_analysis=submission.root_analysis, db=db)

    # Create a second submission tree with a duplicate observable from the first submission
    #
    # submission
    #   o2
    #   o3
    submission2 = factory.submission.create(db=db)
    factory.observable.create_or_read(type="ipv4", value="127.0.0.1", parent_analysis=submission2.root_analysis, db=db)
    factory.observable.create_or_read(
        type="email_address", value="badguy@bad.com", parent_analysis=submission2.root_analysis, db=db
    )

    # Fetching the list of observables in the submissions should only show three observables since
    # there were duplicates. Additionally, they should be sorted by the types then values:
    #
    # email_address: badguy@bad.com
    # fqdn: bad.com
    # ipv4: 127.0.0.1
    result = crud.submission.read_observables(uuids=[submission.uuid, submission2.uuid], db=db)
    assert len(result) == 3
    assert result[0].type.value == "email_address" and result[0].value == "badguy@bad.com"
    assert result[1].type.value == "fqdn" and result[1].value == "bad.com"
    assert result[2].type.value == "ipv4" and result[2].value == "127.0.0.1"


def test_read_submission_tree(db):
    submission = factory.submission.create_from_json_file(
        db=db, json_path="/app/tests/alerts/small.json", submission_name="Test Alert"
    )

    # The small.json submission has 14 observables and 16 analyses (the Root Analysis is not included in the tree).
    result = crud.submission.read_tree(uuid=submission.uuid, db=db)
    assert str(result["children"]).count("'observable'") == 14
    assert str(result["children"]).count("'analysis'") == 16
    assert len(result["children"]) == 2

    # The small.json has three different analysis tags applied to observables, and they should be in alphabetical order.
    assert len(submission.child_analysis_tags) == 3
    assert submission.child_analysis_tags[0].value == "contacted_host"
    assert submission.child_analysis_tags[1].value == "from_address"
    assert submission.child_analysis_tags[2].value == "recipient"

    # The small.json has one permanent tag applied to an observable.
    assert len(submission.child_permanent_tags) == 1
    assert submission.child_permanent_tags[0].value == "c2"

    # The child_tags list should be the alphabetical order of the analysis tags and permanent tags.
    assert len(submission.child_tags) == 4
    assert submission.child_tags[0].value == "c2"
    assert submission.child_tags[1].value == "contacted_host"
    assert submission.child_tags[2].value == "from_address"
    assert submission.child_tags[3].value == "recipient"


def test_sort_by_disposition(db):
    submission1 = factory.submission.create(disposition="disposition1", db=db)
    submission2 = factory.submission.create(disposition="disposition2", db=db)
    submission3 = factory.submission.create(db=db)

    result = crud.submission.read_all(sort="disposition|asc", db=db)
    assert result == [submission1, submission2, submission3]

    result = crud.submission.read_all(sort="disposition|desc", db=db)
    assert result == [submission3, submission2, submission1]


def test_sort_by_disposition_time(db):
    now = crud.helpers.utcnow()

    submission1 = factory.submission.create(disposition="disposition1", update_time=now - timedelta(seconds=5), db=db)
    submission2 = factory.submission.create(disposition="disposition2", update_time=now, db=db)
    submission3 = factory.submission.create(db=db)

    result = crud.submission.read_all(sort="disposition_time|asc", db=db)
    assert result == [submission1, submission2, submission3]

    result = crud.submission.read_all(sort="disposition_time|desc", db=db)
    assert result == [submission3, submission2, submission1]


def test_sort_by_disposition_user(db):
    submission1 = factory.submission.create(disposition="disposition1", updated_by_user="analyst1", db=db)
    submission2 = factory.submission.create(disposition="disposition2", updated_by_user="analyst2", db=db)
    submission3 = factory.submission.create(db=db)

    result = crud.submission.read_all(sort="disposition_user|asc", db=db)
    assert result == [submission1, submission2, submission3]

    result = crud.submission.read_all(sort="disposition_user|desc", db=db)
    assert result == [submission3, submission2, submission1]


def test_sort_by_event_time(db):
    now = crud.helpers.utcnow()

    submission1 = factory.submission.create(event_time=now - timedelta(seconds=5), db=db)
    submission2 = factory.submission.create(event_time=now, db=db)

    result = crud.submission.read_all(sort="event_time|asc", db=db)
    assert result == [submission1, submission2]

    result = crud.submission.read_all(sort="event_time|desc", db=db)
    assert result == [submission2, submission1]


def test_sort_by_insert_time(db):
    now = crud.helpers.utcnow()

    submission1 = factory.submission.create(insert_time=now - timedelta(seconds=5), db=db)
    submission2 = factory.submission.create(insert_time=now, db=db)

    result = crud.submission.read_all(sort="insert_time|asc", db=db)
    assert result == [submission1, submission2]

    result = crud.submission.read_all(sort="insert_time|desc", db=db)
    assert result == [submission2, submission1]


def test_sort_by_name(db):
    submission1 = factory.submission.create(name="submission1", db=db)
    submission2 = factory.submission.create(name="submission2", db=db)

    result = crud.submission.read_all(sort="name|asc", db=db)
    assert result == [submission1, submission2]

    result = crud.submission.read_all(sort="name|desc", db=db)
    assert result == [submission2, submission1]


def test_sort_by_owner(db):
    submission1 = factory.submission.create(owner="analyst1", db=db)
    submission2 = factory.submission.create(owner="analyst2", db=db)

    result = crud.submission.read_all(sort="owner|asc", db=db)
    assert result == [submission1, submission2]

    result = crud.submission.read_all(sort="owner|desc", db=db)
    assert result == [submission2, submission1]


def test_sort_by_queue(db):
    submission1 = factory.submission.create(alert_queue="queue1", db=db)
    submission2 = factory.submission.create(alert_queue="queue2", db=db)

    result = crud.submission.read_all(sort="queue|asc", db=db)
    assert result == [submission1, submission2]

    result = crud.submission.read_all(sort="queue|desc", db=db)
    assert result == [submission2, submission1]


def test_sort_by_type(db):
    submission1 = factory.submission.create(submission_type="type1", db=db)
    submission2 = factory.submission.create(submission_type="type2", db=db)

    result = crud.submission.read_all(sort="submission_type|asc", db=db)
    assert result == [submission1, submission2]

    result = crud.submission.read_all(sort="submission_type|desc", db=db)
    assert result == [submission2, submission1]


def test_tag_functionality(db):
    """
    Submission1
        O1 - permanent_tag1
            A1 - adds tag z_analysis1_tag to O2
                O2 - analysis2_tag, z_analysis1_tag (should show all analysis tags in this alert for the observable)
        O3
            A2 - adds tag analysis2_tag to O2
                O2 - analysis2_tag, z_analysis1_tag (should show all analysis tags in this alert for the observable)

    Submission2
        O1 - should have permanent_tag1 because it is a permanent tag
        O2 - should not have any tags because the alert does not contain analysis A1 or A2
    """

    # Create the submission1 tree structure
    submission1 = factory.submission.create(db=db)

    sub1_o1 = factory.observable.create_or_read(
        type="type1",
        value="value1",
        parent_analysis=submission1.root_analysis,
        permanent_tags=["permanent_tag1"],
        db=db,
    )

    amt1 = factory.analysis_module_type.create_or_read(value="amt1", db=db)
    o1_a1 = factory.analysis.create_or_read(analysis_module_type=amt1, submission=submission1, target=sub1_o1, db=db)

    a1_o2 = factory.observable.create_or_read(
        type="type2", value="value2", parent_analysis=o1_a1, analysis_tags=["z_analysis1_tag"], db=db
    )

    sub1_o3 = factory.observable.create_or_read(
        type="type3", value="value3", parent_analysis=submission1.root_analysis, db=db
    )

    amt2 = factory.analysis_module_type.create_or_read(value="amt2", db=db)
    o3_a2 = factory.analysis.create_or_read(analysis_module_type=amt2, submission=submission1, target=sub1_o3, db=db)

    a2_o2 = factory.observable.create_or_read(
        type="type2", value="value2", parent_analysis=o3_a2, analysis_tags=["analysis2_tag"], db=db
    )

    # Create the submission2 tree structure
    submission2 = factory.submission.create(db=db)

    sub2_o1 = factory.observable.create_or_read(
        type="type1", value="value1", parent_analysis=submission2.root_analysis, db=db
    )

    sub2_o2 = factory.observable.create_or_read(
        type="type2", value="value2", parent_analysis=submission2.root_analysis, db=db
    )

    # The two instances of O1 across both submissions should be the same observable
    assert sub1_o1.uuid == sub2_o1.uuid

    # The two instances of O1 should both have the permanent_tag1 tag
    assert len(sub1_o1.permanent_tags) == 1
    assert sub1_o1.permanent_tags[0].value == "permanent_tag1"
    assert len(sub2_o1.permanent_tags) == 1
    assert sub2_o1.permanent_tags[0].value == "permanent_tag1"

    # The three instances of O2 across both submissions should be the same observable
    assert a1_o2.uuid == a2_o2.uuid == sub2_o2.uuid

    # The analysis tags are only associated with their observables when the submission tree is constructed
    submission1_tree = crud.submission.read_tree(submission1.uuid, db=db)
    submission2_tree = crud.submission.read_tree(submission2.uuid, db=db)

    # The first submission should have two child observables, and they should be in the order
    # in which they were added to the tree (they are not sorted).
    assert len(submission1_tree["children"]) == 2
    assert submission1_tree["children"][0]["uuid"] == str(sub1_o1.uuid)
    assert submission1_tree["children"][1]["uuid"] == str(sub1_o3.uuid)

    # Verify the tags for O1 in the first submission
    assert len(submission1_tree["children"][0]["permanent_tags"]) == 1
    assert submission1_tree["children"][0]["permanent_tags"][0]["value"] == "permanent_tag1"

    # Verify the tags for O2 in the first submission under A1. It should have two tags, even though
    # its parent analysis A1 only added one tag. The tags should be in alphabetical order, not the
    # order in which they were added by the analyses.
    assert len(o1_a1.analysis_metadata) == 1
    assert o1_a1.analysis_metadata[0].metadata_object.value == "z_analysis1_tag"
    assert len(submission1_tree["children"][0]["children"][0]["children"][0]["metadata"]) == 2
    assert submission1_tree["children"][0]["children"][0]["children"][0]["metadata"][0]["value"] == "analysis2_tag"
    assert submission1_tree["children"][0]["children"][0]["children"][0]["metadata"][1]["value"] == "z_analysis1_tag"

    # Verify the tags for O2 in the first submission under A2. It should have two tags, even though
    # its parent analysis A2 only added one tag. The tags should be in alphabetical order, not the
    # order in which they were added by the analyses.
    assert len(o3_a2.analysis_metadata) == 1
    assert o3_a2.analysis_metadata[0].metadata_object.value == "analysis2_tag"
    assert len(submission1_tree["children"][1]["children"][0]["children"][0]["metadata"]) == 2
    assert submission1_tree["children"][1]["children"][0]["children"][0]["metadata"][0]["value"] == "analysis2_tag"
    assert submission1_tree["children"][1]["children"][0]["children"][0]["metadata"][1]["value"] == "z_analysis1_tag"

    # The second submission should have two child observables, and they should be in the order
    # in which they were added to the tree (they are not sorted).
    assert len(submission2_tree["children"]) == 2
    assert submission2_tree["children"][0]["uuid"] == str(sub2_o1.uuid)
    assert submission2_tree["children"][1]["uuid"] == str(sub2_o2.uuid)

    # Verify the tags for O1 in the second submission
    assert len(submission2_tree["children"][0]["permanent_tags"]) == 1
    assert submission2_tree["children"][0]["permanent_tags"][0]["value"] == "permanent_tag1"

    # Verify the tags for O2 in the second submission. Even though it is the exact same observable
    # object as in the first submission, it shouldn't have any tags because the submission does not
    # contain any analysis that added tags to it.
    assert len(submission2_tree["children"][1]["metadata"]) == 0
    assert len(submission2_tree["children"][1]["permanent_tags"]) == 0
