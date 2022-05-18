from ace2.core.observables import *

def test_uri_path():
    # create an observable
    observable = UriPath('/yada/yada/yada')

    # verify attributes
    assert observable.type == 'uri_path'
    assert observable.value == '/yada/yada/yada'

    # save then load
    state = observable.dict()
    observable = Observable(**state)

    # verify class instatnce
    assert isinstance(observable, UriPath)
    assert observable.type == 'uri_path'
    assert observable.value == '/yada/yada/yada'
