from ace2.core.observables import *

def test_ipv4():
    # create an observable
    observable = Ipv4('127.0.0.1')

    # verify attributes
    assert observable.type == 'ipv4'
    assert observable.value == '127.0.0.1'

    # save then load
    state = observable.dict()
    observable = Observable(**state)

    # verify class instatnce
    assert isinstance(observable, Ipv4)
    assert observable.type == 'ipv4'
    assert observable.value == '127.0.0.1'
