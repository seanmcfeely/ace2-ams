from ace2 import *

def test_fqdn():
    # create an observable
    observable = FQDN('www.google.com')

    # verify attributes
    assert observable.type == 'fqdn'
    assert observable.value == 'www.google.com'

    # save then load
    state = observable.dict()
    observable = Observable(**state)

    # verify class instatnce
    assert isinstance(observable, FQDN)
    assert observable.type == 'fqdn'
    assert observable.value == 'www.google.com'
