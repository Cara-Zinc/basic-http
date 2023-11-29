class HttpTransaction:

    def __init__(self):
        self._version = 'HTTP/1.1'
        self._headers = {}
        self._body = b''

    def __repr__(self):
        return f'{self._version} with headers {self._headers} and body {self._body}'

    @property
    def version(self):
        return self._version

    @property
    def headers(self):
        return self._headers.copy()

    @property
    def body(self):
        return self._body
