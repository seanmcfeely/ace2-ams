from ace2 import *

def test_directive():
    # load directive from state
    state = {
        'type': 'directive',
        'value': 'foo',
    }
    metadata = Metadata(**state)
    assert isinstance(metadata, Directive)
    assert metadata.type == 'directive'
    assert metadata.value == 'foo'
    assert metadata.dict() == state

    # create directive
    metadata = Directive('foo')
    assert metadata.type == 'directive'
    assert metadata.value == 'foo'
    assert metadata.dict() == state
