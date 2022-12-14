import json
import pytest
import uuid

from fastapi import status

from db.tests import factory


#
# INVALID TESTS
#


@pytest.mark.parametrize(
    "key,value",
    [
        ("cache_seconds", None),
        ("cache_seconds", ""),
        ("cache_seconds", "abc"),
        ("cache_seconds", "1"),
        ("description", 123),
        ("description", ""),
        ("extended_version", 123),
        ("extended_version", ""),
        ("extended_version", []),
        ("manual", 123),
        ("manual", None),
        ("manual", "True"),
        ("observable_types", 123),
        ("observable_types", None),
        ("observable_types", "test_type"),
        ("observable_types", [123]),
        ("observable_types", [None]),
        ("observable_types", [""]),
        ("observable_types", ["abc", 123]),
        ("required_directives", 123),
        ("required_directives", None),
        ("required_directives", "test_type"),
        ("required_directives", [123]),
        ("required_directives", [None]),
        ("required_directives", [""]),
        ("required_directives", ["abc", 123]),
        ("required_tags", 123),
        ("required_tags", None),
        ("required_tags", "test_type"),
        ("required_tags", [123]),
        ("required_tags", [None]),
        ("required_tags", [""]),
        ("required_tags", ["abc", 123]),
        ("value", 123),
        ("value", None),
        ("value", ""),
        ("version", 123),
        ("version", None),
        ("version", ""),
        ("version", "v1.0"),
    ],
)
def test_update_invalid_fields(client, key, value):
    update = client.patch(f"/api/analysis/module_type/{uuid.uuid4()}", json={key: value})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_invalid_uuid(client):
    update = client.patch("/api/analysis/module_type/1", json={"value": "test_type"})
    assert update.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_duplicate_value_version(client, db):
    # Create some objects
    factory.analysis_module_type.create_or_read(value="test", version="1.0.0", db=db)
    amt2 = factory.analysis_module_type.create_or_read(value="test", version="1.0.1", db=db)

    # Ensure you cannot update an analysis module type to have a duplicate version+value combination
    update = client.patch(f"/api/analysis/module_type/{amt2.uuid}", json={"version": "1.0.0"})
    assert update.status_code == status.HTTP_400_BAD_REQUEST


def test_update_nonexistent_uuid(client):
    update = client.patch(f"/api/analysis/module_type/{uuid.uuid4()}", json={"value": "test"})
    assert update.status_code == status.HTTP_404_NOT_FOUND


#
# VALID TESTS
#


@pytest.mark.parametrize(
    "key,values",
    [
        ("observable_types", []),
        ("observable_types", ["test"]),
        ("observable_types", ["test1", "test2"]),
        ("observable_types", ["test", "test"]),
        ("required_directives", []),
        ("required_directives", ["test"]),
        ("required_directives", ["test1", "test2"]),
        ("required_directives", ["test", "test"]),
        ("required_tags", []),
        ("required_tags", ["test"]),
        ("required_tags", ["test1", "test2"]),
        ("required_tags", ["test", "test"]),
    ],
)
def test_update_valid_list_fields(client, db, key, values):
    # Create an analysis module type
    analysis_module_type = factory.analysis_module_type.create_or_read(value="test_type", db=db)

    # Create the objects
    if key == "observable_types":
        create_func = factory.observable_type.create_or_read
    elif key == "required_directives":
        create_func = factory.metadata_directive.create_or_read
    else:
        create_func = factory.metadata_tag.create_or_read

    for value in values:
        create_func(value=value, db=db)

    # Update it
    update = client.patch(f"/api/analysis/module_type/{analysis_module_type.uuid}", json={key: values})
    assert update.status_code == status.HTTP_204_NO_CONTENT
    assert len(getattr(analysis_module_type, key)) == len(set(values))


@pytest.mark.parametrize(
    "key,initial_value,updated_value",
    [
        ("cache_seconds", 90, 3600),
        ("cache_seconds", 90, 90),
        ("description", None, "test"),
        ("description", "test", "test"),
        ("extended_version", None, '{"foo": "bar"}'),
        ("extended_version", '{"foo": "bar"}', '{"foo": "bar"}'),
        ("manual", True, False),
        ("manual", False, False),
        ("value", "test", "test2"),
        ("value", "test", "test"),
        ("version", "1.0.0", "1.0.1"),
        ("version", "1.0.0", "1.0.0"),
    ],
)
def test_update(client, db, key, initial_value, updated_value):
    # Create an analysis module type
    analysis_module_type = factory.analysis_module_type.create_or_read(value="test_type", db=db)

    # Set the initial value
    setattr(analysis_module_type, key, initial_value)

    # Update it
    update = client.patch(f"/api/analysis/module_type/{analysis_module_type.uuid}", json={key: updated_value})
    assert update.status_code == status.HTTP_204_NO_CONTENT

    if key == "extended_version":
        assert analysis_module_type.extended_version == json.loads(updated_value)
    else:
        assert getattr(analysis_module_type, key) == updated_value
