import io
import json
import logging
from enum import Enum, unique, auto

from HttpTransaction import *


@unique
class HttpMethod(Enum):
    GET = auto()
    POST = auto()
    HEAD = auto()


class HttpRequest(HttpTransaction):
    @staticmethod
    def receive_requests(sin: io.BufferedReader):
        while True:
            request = HttpRequest()
            try:
                line = ''
                empty_line_count = 0
                while True:
                    line = sin.readline().decode('utf-8').strip()
                    if line:
                        break

                    empty_line_count += 1
                    if empty_line_count >= 10:
                        sin.close()
                        return

                method, query, version = line.split(' ')
                _path, param = query.split('?') if '?' in query else (query, '')
                request._method = HttpMethod[method.upper()]
                request._path = path(_path)
                request._version = version

                if param:
                    for p in param.split('&'):
                        key, value = p.split('=') if '=' in p else (p, '')
                        request._parameter[key] = value

                while True:
                    header = sin.readline().decode('utf-8').strip()
                    if not header:
                        break

                    key, value = header.split(': ')
                    key = key.strip()
                    value = value.strip()
                    request._headers[key] = value

                    if key == 'Cookie':
                        for cookie in value.split('; '):
                            key, value = cookie.split('=')
                            request._cookies[key] = value

                request._raw_body = sin.read(int(request._headers.get('Content-Length', 0)))
                body_type = request._headers.get('Content-Type', 'text/plain')
                if body_type == 'text/plain':
                    request._body = request._raw_body.decode('utf-8')
                elif body_type == 'application/json':
                    request._body = json.loads(request._raw_body.decode('utf-8'))
                else:
                    request._body = request._raw_body

                yield request
            except Exception as e:
                logging.exception(e)

            if request._headers['Connection'] == 'close' or sin.closed:
                return

    def __init__(self):
        super().__init__()
        self._method: HttpMethod = HttpMethod.GET
        self._path = tuple()
        self._parameter = {}
        self._cookies = {}

        self._headers['Connection'] = 'keep-alive'

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path

    @property
    def parameter(self):
        return self._parameter.copy()

    @property
    def cookies(self):
        return self._cookies.copy()
