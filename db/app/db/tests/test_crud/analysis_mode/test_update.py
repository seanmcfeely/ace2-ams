from api_models.analysis_mode import AnalysisModeUpdate
from db import crud
from db.tests import factory


def test_update(db):
    factory.analysis_module_type.create_or_read(value="module1", version="1.0.0", db=db)
    factory.analysis_module_type.create_or_read(value="module1", version="2.0.0", db=db)
    factory.analysis_module_type.create_or_read(value="module2", version="1.0.0", db=db)

    obj = factory.analysis_mode.create_or_read(analysis_module_types=["module1", "module2"], value="test", db=db)

    assert len(obj.analysis_module_types) == 2
    assert any(m.value == "module1" and m.version == "2.0.0" for m in obj.analysis_module_types)
    assert any(m.value == "module2" and m.version == "1.0.0" for m in obj.analysis_module_types)
    assert obj.description is None
    assert obj.value == "test"

    factory.analysis_module_type.create_or_read(value="module3", version="1.0.0", db=db)

    crud.analysis_mode.update(
        uuid=obj.uuid,
        model=AnalysisModeUpdate(
            analysis_module_types=["module2", "module3"], description="test description", value="new value"
        ),
        db=db,
    )

    assert len(obj.analysis_module_types) == 2
    assert any(m.value == "module2" and m.version == "1.0.0" for m in obj.analysis_module_types)
    assert any(m.value == "module3" and m.version == "1.0.0" for m in obj.analysis_module_types)
    assert obj.description == "test description"
    assert obj.value == "new value"


def test_update_duplicate_value(db):
    obj1 = factory.analysis_mode.create_or_read(value="test", db=db)
    obj2 = factory.analysis_mode.create_or_read(value="test2", db=db)

    result = crud.analysis_mode.update(uuid=obj2.uuid, model=AnalysisModeUpdate(value=obj1.value), db=db)
    assert result is False
