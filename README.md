# ACE2 Service Library
This library provides base classes for creating new ACE2 services such as analysis and collectors.

## Installation
```bash
python3 -m pip install git+ssh://git@github.info53.com/Fifth-Third/ice2.git
```

## Testing
Clone the repo
```bash
git clone git@github.info53.com:Fifth-Third/ice2.git
```

Install tox if it is not already installed
```bash
python3 -m pip install tox
```

Run tox from the project root dir with the recreate options to install any newly added dependencies
```bash
cd ace2
tox -r
```

## Analysis
The following is an example of how to make a new Analysis subclass
```python
from ace2 import *

class MyAnalysis(Analysis):
    def execute_analysis(self, observable):
        # pretend to submit something to a service using state to store non analysis info
        self.state['search_id'] = '123'
        
        # wait a second then get the results
        return Callback(self.get_results, seconds=1)

    def get_results(self, observable):
        # add generic analysis details
        self.details['foo'] = 'bar'

        # add analysis details via custom analysis class
        self.results = '127.0.0.1'

        # add child observable to analysis
        observable = self.add(Ipv4, self.analysis.results)

        # add generic metadata with type='hello' and value='world' to child observable
        observable.add(Metadata, 'hello', 'world')

        # add 'beep' tag to child observable
        observable.add(Tag, 'beep')

        # set the analysis summary
        self.summary = f'My Analysis = {self.analysis.results}'

        # no return means analysis is complete
```
