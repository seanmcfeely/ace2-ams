from ace2.core import *

class MyAnalysis(Analysis):
    def execute(self, observable):
        # verify observable is passed correctly
        assert isinstance(observable, Ipv4)
        assert observable.type == 'ipv4'
        assert observable.value == '127.0.0.1'

        # pretend that we submitted something to a sandbox or whatever
        self.state['submission_id'] = '123'

        # check back later
        return Callback(self.get_results)

    def get_results(self, observable):
        # verify observable is passed correctly
        assert isinstance(observable, Ipv4)
        assert observable.type == 'ipv4'
        assert observable.value == '127.0.0.1'

        # make sure the state was kept
        assert self.state['submission_id'] == '123'

        # add some details
        self.details['result'] = 'its malz bro'

        # add a generic child observable
        observable = self.add(Observable, 'foo', 'bar')
        assert len(self.observables) == 1
        assert isinstance(observable, Observable)
        assert observable.type == 'foo'
        assert observable.value == 'bar'

        # ensure duplicate observables are not added
        observable = self.add(Observable, 'foo', 'bar')
        assert len(self.observables) == 1

        # add a typed child observble
        observable = self.add(Ipv4, '127.0.0.1')
        assert len(self.observables) == 2
        assert isinstance(observable, Ipv4)
        assert observable.type == 'ipv4'
        assert observable.value == '127.0.0.1'

        # set the summary
        self.summary = f'hey, {self.details["result"]}'

def test_analysis(monkeypatch, mock_datetime):
    # create analysis to run
    analysis = {
        'id': 1,
        'type': 'my_analysis',
        'target': {
            'type': 'ipv4',
            'value': '127.0.0.1',
        },
    }

    # run the analysis with the lambda handler function
    analysis = MyAnalysis.run(analysis, None)

    # verify result
    assert analysis == {
        'id': 1,
        'type': 'my_analysis',
        'target': {
            'type': 'ipv4',
            'value': '127.0.0.1',
            'metadata': [],
        },
        'summary': None,
        'details': {},
        'observables': [],
        'callback': {
            'method': 'get_results',
            'timestamp': mock_datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        },
        'state': {
            'submission_id': '123',
        },
    }

    # run again to test the callback
    analysis = MyAnalysis.run(analysis, None)

    # verify result
    assert analysis == {
        'id': 1,
        'type': 'my_analysis',
        'target': {
            'type': 'ipv4',
            'value': '127.0.0.1',
            'metadata': [],
        },
        'summary': 'hey, its malz bro',
        'details': {
            'result': 'its malz bro',
        },
        'observables': [
            {
                'type': 'foo',
                'value': 'bar',
                'metadata': [],
            },
            {
                'type': 'ipv4',
                'value': '127.0.0.1',
                'metadata': [],
            },
        ],
        'callback': None,
        'state': {
            'submission_id': '123',
        },
    }
