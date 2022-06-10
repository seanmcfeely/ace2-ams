from api_models.node_directive import NodeDirectiveUpdate
from db import crud
from tests import factory


def test_update(db):
    obj = factory.node_directive.create_or_read(value="test", db=db)

    assert obj.description is None
    assert obj.value == "test"

    crud.node_directive.update(
        uuid=obj.uuid,
        model=NodeDirectiveUpdate(description="test description", value="new value"),
        db=db,
    )

    assert obj.description == "test description"
    assert obj.value == "new value"


def test_update_duplicate_value(db):
    obj1 = factory.node_directive.create_or_read(value="test", db=db)
    obj2 = factory.node_directive.create_or_read(value="test2", db=db)

    result = crud.node_directive.update(uuid=obj2.uuid, model=NodeDirectiveUpdate(value=obj1.value), db=db)
    assert result is False
