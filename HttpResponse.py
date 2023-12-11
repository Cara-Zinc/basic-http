import io
import json
from datetime import datetime, timezone
from enum import Enum, unique
from typing import Literal

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


class Cookie:
    def __init__(self, key: str, value: str, **kwargs):
        self.key = key
        self.value = value

        self.domain: str | None = kwargs.get('domain', None)
        self.path: str | None = kwargs.get('path', None)

        self.max_age: int | None = kwargs.get('max_age', None)
        self.expires: datetime | None = kwargs.get('expires', None)

        self.http_only: bool = kwargs.get('http_only', False)
        self.secure: bool = kwargs.get('secure', False)

        self.partitioned: bool = kwargs.get('partitioned', False)

        self.same_site: Literal['Strict', 'Lax', 'None', None] = kwargs.get('same_site', None)

    def __str__(self):
        args = [f'{self.key}={self.value}']

        if self.domain:
            args.append(f'Domain={self.domain}')
        if self.path:
            args.append(f'Path={self.path}')

        if self.max_age:
            args.append(f'Max-Age={self.max_age}')
        if self.expires:
            args.append(f'Expires={self.expires.astimezone(timezone.utc):%a, %d %b %Y %H:%M:%S GMT}')

        if self.http_only:
            args.append('HttpOnly')
        if self.secure or self.same_site == 'None':
            args.append('Secure')

        if self.partitioned:
            args.append('Partitioned')

        if self.same_site:
            args.append(f'SameSite={self.same_site}')

        return '; '.join(args)

    def __repr__(self):
        return f'Cookie({self!s})'


class HttpResponse(HttpTransaction):
    def __init__(self):
        super().__init__()
        self.code = HttpStatus.OK
        self._headers['Connection'] = 'keep-alive'
        self._cookies: dict[str, Cookie] = {}

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

    def cookie(self, cookie: Cookie):
        self._cookies[cookie.key] = cookie

    def send(self, sout: io.BufferedWriter):
        lines = [f'{self._version} {self.code.code} {self.code.message}'.encode('utf-8')]
        for key, value in self._headers.items():
            lines.append(f'{key}: {value}'.encode('utf-8'))

        for cookie in self._cookies.values():
            lines.append(f'Set-Cookie: {cookie!s}'.encode('utf-8'))

        lines.append(b'')
        lines.append(self._body)

        sout.write(b'\r\n'.join(lines))
        sout.write(b'\r\n')

        sout.flush()
