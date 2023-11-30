import io
import json
from enum import Enum, unique

from HttpTransaction import HttpTransaction


@unique
class HttpStatus(Enum):
    OK = 200, 'OK'
    PARTIAL_CONTENT = 206, 'Partial Content'

    REDIRECT = 301, 'Moved Permanently'

    BAD_REQUEST = 400, 'Bad Request'
    UNAUTHORIZED = 401, 'Unauthorized'
    FORBIDDEN = 403, 'Forbidden'
    NOT_FOUND = 404, 'Not Found'
    METHOD_NOT_ALLOWED = 405, 'Method Not Allowed'
    RANGE_NOT_SATISFIABLE = 416, 'Range Not Satisfiable'

    INTERNAL_SERVER_ERROR = 500, 'Internal Server Error'
    BAD_GATEWAY = 502, 'Bad Gateway'
    SERVICE_UNAVAILABLE = 503, 'Service Unavailable'

    def __init__(self, code: int, message: str):
        super().__init__()
        self.code = code
        self.message = message


class HttpResponse(HttpTransaction):

    def __init__(self):
        super().__init__()
        self.code = HttpStatus.OK
        self._headers['Connection'] = 'keep-alive'

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value: str | bytes | dict):
        if isinstance(value, str):
            self._body = value.encode('utf-8')
            self._headers['Content-Type'] = 'text/plain'
        elif isinstance(value, bytes):
            self._body = value
            self._headers['Content-Type'] = 'application/octet-stream'
        elif isinstance(value, dict):
            self._body = json.dumps(value).encode('utf-8')
            self._headers['Content-Type'] = 'application/json'

        self.headers['Content-Length'] = len(self._body)

    @property
    def headers(self):
        return self._headers

    def send(self, sout: io.BufferedWriter):
        lines = [f'{self._version} {self.code.code} {self.code.message}'.encode('utf-8')]
        for key, value in self._headers.items():
            lines.append(f'{key}: {value}'.encode('utf-8'))
        lines.append(b'')
        lines.append(self._body)

        sout.write(b'\r\n'.join(lines))
        sout.write(b'\r\n')

        sout.flush()
