from ace2 import *

def test_observable():
    # create an observable from constructor
    observable = Observable('foo', 'bar')

    # verify attributes
    assert observable.type == 'foo'
    assert observable.value == 'bar'
    assert observable.key == 'foo|bar'

    # add tag
    observable.add(Tag, 'beep')
    assert len(observable.tags) == 1
    assert 'beep' in observable.tags
    assert isinstance(observable.metadata[0], Tag)

    # make sure duplicates are not added
    observable.add(Tag, 'beep')
    assert len(observable.tags) == 1

    # verify saving works
    state = observable.dict() 
    assert state == {
        'type': 'foo',
        'value': 'bar',
        'metadata': [
            {
                'type': 'tag',
                'value': 'beep',
            },
        ],
    }

    # load observable from state
    observable2 = Observable(**state)

    # verify attributes
    assert observable2.type == 'foo'
    assert observable2.value == 'bar'
    assert observable2.key == 'foo|bar'
    assert 'beep' in observable2.tags

    # verify observables are considered equal
    assert observable == observable2

    # test display value
    assert observable.display_value == observable.value
    observable.add(DisplayValue, 'hello')
    assert observable.display_value == 'hello'

    # test adding new observable type
    class Hello(Observable):
        def __init__(self, value, **kwargs):
            super().__init__(self.type, value, **kwargs)
    observable = Observable('hello', 'world')
    assert isinstance(observable, Hello)
    assert observable.type == 'hello'
    assert observable.value == 'world'

    # add directive
    observable.add(Directive, 'just do it')
    assert 'just do it' in observable.directives
