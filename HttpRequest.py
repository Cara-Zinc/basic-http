import io
import logging
import typing

from HttpTransaction import HttpTransaction


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

                method, path, version = line.split(' ')
                request._method = method.upper()
                request._path = path.removeprefix('/').split('/')
                request._version = version

                while True:
                    header = sin.readline().decode('utf-8').strip()
                    if not header:
                        break

                    key, value = header.split(': ')
                    request._headers[key] = value.strip()

                request._body_length = int(request._headers.get('Content-Length', 0))
                request._body = sin.read(request._body_length).decode('utf-8')

                yield request
            except Exception as e:
                logging.exception(e)

            if request._headers['Connection'] == 'close' or sin.closed:
                return

    def __init__(self):
        super().__init__()
        self._method: typing.Literal['GET', 'POST', 'HEAD'] = 'GET'
        self._path = tuple()

        self._headers['Connection'] = 'keep-alive'

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path
