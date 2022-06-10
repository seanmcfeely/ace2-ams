from db import crud
from tests import factory


def test_read_all(db):
    factory.node_threat.create_or_read(value="test1", db=db)
    factory.node_threat.create_or_read(value="test2", db=db)

    result = crud.node_threat.read_all(db=db)
    assert len(result) == 2
    assert result[0].value == "test1"
    assert result[1].value == "test2"
