def path(_path: str) -> list[str]:
    return _path.removeprefix('/').split('/')

class HttpTransaction:

    def __init__(self):
        self._version: str = 'HTTP/1.1'
        self._headers: dict = {}
        self._raw_body: bytes = b''
        self._body = ''
        self._headers['Content-Type'] = 'text/plain'

    def __repr__(self):
        return f'{self._version} with headers {self._headers} and body {self._raw_body}'

    @property
    def version(self):
        return self._version

    @property
    def headers(self):
        return self._headers.copy()

    @property
    def body(self):
        return self._body
