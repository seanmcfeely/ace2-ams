from api_models.analysis_mode import AnalysisModeCreate
from db import crud
from db.tests import factory


def test_create(db):
    # Create some analysis module types. Only the latest version ones will be used.
    factory.analysis_module_type.create_or_read(value="module1", version="1.0.0", db=db)
    factory.analysis_module_type.create_or_read(value="module1", version="2.0.0", db=db)
    factory.analysis_module_type.create_or_read(value="module2", version="1.0.0", db=db)
    factory.analysis_module_type.create_or_read(value="module2", version="2.0.0", db=db)

    obj = crud.analysis_mode.create_or_read(
        model=AnalysisModeCreate(value="test value", analysis_module_types=["module1", "module2"]), db=db
    )

    assert len(obj.analysis_module_types) == 2
    assert any(m.value == "module1" and m.version == "2.0.0" for m in obj.analysis_module_types)
    assert any(m.value == "module2" and m.version == "2.0.0" for m in obj.analysis_module_types)
    assert obj.description is None
    assert obj.value == "test value"


def test_create_duplicate_value(db):
    obj1 = crud.analysis_mode.create_or_read(model=AnalysisModeCreate(value="test"), db=db)
    assert obj1

    # Ensure that you get the same object back if you try to create a duplicate value
    obj2 = crud.analysis_mode.create_or_read(model=AnalysisModeCreate(value=obj1.value), db=db)
    assert obj2.description == obj1.description
    assert obj2.uuid == obj1.uuid
    assert obj2.value == obj1.value
