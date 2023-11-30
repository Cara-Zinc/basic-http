import logging
import socket
import threading
from typing import Callable

from HttpRequest import HttpRequest, HttpMethod
from HttpResponse import HttpResponse, HttpStatus
from HttpTransaction import path


class HttpServer:

    def __init__(self):
        self._server_socket: socket.socket = socket.socket(type=socket.SOCK_STREAM)
        self._routing: dict = {
            ('',): {
                HttpMethod.GET: {
                    'handler': HttpServer.welcome_handler
                }
            }
        }

    def __handler(self, s: socket.socket, addr: str):
        try:
            with s.makefile('rb', encoding='utf-8') as sin, s.makefile('wb', encoding='utf-8') as sout:
                for request in HttpRequest.receive_requests(sin):
                    logging.debug(request)
                    response = HttpResponse()
                    route = self.get_route(request.path, request.method)
                    handler = route['handler'] if route else HttpServer.default_handler
                    try:
                        handler(request, response)
                    except:
                        response = HttpResponse()
                        HttpServer.error_handler(request, response)
                    response.send(sout)
        finally:
            s.close()

    def listen(self, host: str, port: int):
        self._server_socket.bind((host, port))
        self._server_socket.listen()
        try:
            while True:
                s, addr = self._server_socket.accept()
                threading.Thread(target=self.__handler, args=(s, addr)).start()
        except KeyboardInterrupt:
            pass
        finally:
            self._server_socket.close()

    def route(self, _path: str | list[str] | tuple[str], method: HttpMethod,
              handler: Callable[[HttpRequest, HttpResponse], None]):
        if isinstance(_path, str):
            _path = path(_path)
        if isinstance(_path, list):
            _path = tuple(_path)

        route_path = self._routing.get(_path, {})
        route_path[method] = {'handler': handler}

    def get(self, _path: str | list[str] | tuple[str], handler: Callable[[HttpRequest, HttpResponse], None]):
        self.route(_path, HttpMethod.GET, handler)

    def post(self, _path: str | list[str] | tuple[str], handler: Callable[[HttpRequest, HttpResponse], None]):
        self.route(_path, HttpMethod.POST, handler)

    def head(self, _path: str | list[str] | tuple[str], handler: Callable[[HttpRequest, HttpResponse], None]):
        self.route(_path, HttpMethod.HEAD, handler)

    def get_route(self, _path: str | list[str] | tuple[str], method: HttpMethod):
        if isinstance(_path, str):
            _path = path(_path)
        if isinstance(_path, list):
            _path = tuple(_path)

        if _path not in self._routing:
            return None

        route_path = self._routing[_path]

        if method not in route_path:
            return None

        return route_path[method]

    @staticmethod
    def welcome_handler(request: HttpRequest, response: HttpResponse):
        response.body = '''
            <html lang="en-us">
                <head>
                    <title>Welcome to the Basic Http Engine!</title>
                </head>
                <body>
                    <h1>Welcome to the Basic Http Engine!</h1>
                    <hr />
                    <p>
                        If you see this page, it means that the server is running properly.
                    </p>
                    <p>
                        Consider adding more pages to beautify your website.
                    </p>
                </body>
            </html>
        '''
        response.headers['Content-Type'] = 'text/html'

    @staticmethod
    def default_handler(request: HttpRequest, response: HttpResponse):
        response.code = HttpStatus.NOT_FOUND
        response.body = '''
            <html lang="en-us">
                <head>
                    <title>404 Not Found</title>
                </head>
                <body>
                    <h1>404 Not Found</h1>
                    <hr />
                    <p>
                        Sorry, the resource you requested is not found.
                    </p>
                </body>
            </html>
        '''
        response.headers['Content-Type'] = 'text/html'

    @staticmethod
    def error_handler(request: HttpRequest, response: HttpResponse):
        response.code = HttpStatus.INTERNAL_SERVER_ERROR
        response.body = '''
            <html lang="en-us">
                <head>
                    <title>500 Internal Server Error</title>
                </head>
                <body>
                    <h1>500 Internal Server Error</h1>
                    <hr />
                    <p>
                        Sorry, the server encountered an exception while handling your request.
                    </p>
                    <p>
                        If the problem persists, please contact the administrator.
                    </p>
                </body>
            </html>
        '''
        response.headers['Content-Type'] = 'text/html'
