from db import crud
from tests import factory


def test_read_all(db):
    factory.analysis_module_type.create_or_read(value="module1", db=db)
    factory.analysis_module_type.create_or_read(value="module2", db=db)

    result = crud.analysis_module_type.read_all(db=db)
    assert len(result) == 2
    assert result[0].value == "module1"
    assert result[1].value == "module2"


def test_read_by_values_latest_version(db):
    factory.analysis_module_type.create_or_read(value="module1", version="1.0.0", db=db)
    factory.analysis_module_type.create_or_read(value="module1", version="2.0.0", db=db)
    factory.analysis_module_type.create_or_read(value="module2", version="1.0.0", db=db)
    factory.analysis_module_type.create_or_read(value="module2", version="2.0.0", db=db)

    # Test getting a single analysis module type
    result = crud.analysis_module_type.read_by_values_latest_version(values=["module1"], db=db)
    assert len(result) == 1
    assert result[0].value == "module1" and result[0].version == "2.0.0"

    # Test getting multiple analysis module types
    result = crud.analysis_module_type.read_by_values_latest_version(values=["module1", "module2"], db=db)
    assert len(result) == 2
    assert result[0].value == "module1" and result[0].version == "2.0.0"
    assert result[1].value == "module2" and result[1].version == "2.0.0"
