import pytest

from uuid import uuid4

from api_models.alert_disposition import AlertDispositionCreate
from db import crud


@pytest.mark.parametrize(
    "key",
    [
        ("rank"),
        ("uuid"),
        ("value"),
    ],
)
def test_create_duplicate_unique_fields(db, key):
    # Create an object
    params1 = {"rank": 1, "value": "test", "uuid": uuid4()}
    obj1 = crud.alert_disposition.create_or_read(model=AlertDispositionCreate(**params1), db=db)
    assert obj1

    # Ensure that you get the same object back if you try to create another one
    # with a duplicate field that needs to be unique.
    params2 = {"rank": 2, "value": "test2", "uuid": uuid4()}
    params2[key] = params1[key]
    obj2 = crud.alert_disposition.create_or_read(model=AlertDispositionCreate(**params2), db=db)
    assert obj2
    assert obj2.description == obj1.description
    assert obj2.rank == obj1.rank
    assert obj2.uuid == obj1.uuid
    assert obj2.value == obj1.value
