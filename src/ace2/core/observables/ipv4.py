from .observable import Observable

class IPv4(Observable):
    ''' Observable that represents an internet protocol version 4 address '''

    def __init__(self, value:str, **kwargs):
        ''' Initializes an ipv4 observable

        Args:
            value (str): the ipv4
        '''

        # call super class constructor with our type and given value
        super().__init__(self.type, value, **kwargs)
