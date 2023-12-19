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
                        request._parameters[key] = value

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
        self._path: list[str] = []
        self._parameters: dict[str, str] = {}
        self._cookies: dict[str, str] = {}

        self._path_variables: dict[str, str] = {}
        self._path_variables_set: bool = False

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path

    @property
    def parameters(self):
        return self._parameters.copy()

    @property
    def cookies(self):
        return self._cookies.copy()

    @property
    def path_variables(self):
        return self._path_variables.copy()

    @path_variables.setter
    def path_variables(self, value: dict[str, str]):
        if self._path_variables_set:
            raise Exception('Path variable has already been set')

        self._path_variables = value
        self._path_variables_set = True
