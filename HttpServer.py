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
        self._default_handler = HttpServer.default_handler
        self._error_handler = HttpServer.error_handler
        self._routing: dict = {}
        self.get("/", HttpServer.welcome_handler)

    # noinspection PyTestUnpassedFixture
    def __handler(self, s: socket.socket, addr: str):
        try:
            with s.makefile("rb", encoding="utf-8") as sin, s.makefile(
                    "wb", encoding="utf-8"
            ) as sout:
                for request in HttpRequest.receive_requests(sin):
                    logging.info(request)
                    response = HttpResponse()

                    if request.headers["Connection"] == "close":
                        response.headers["Connection"] = "close"

                    route = self.get_route(request.path, request.method) or {
                        "handler": self._default_handler,
                        "path_variables": {},
                    }
                    handler = route["handler"] if route else self._default_handler

                    path_variables = {}
                    if "path_variables" in route:
                        for k, v in route["path_variables"].items():
                            path_variables[v] = request.path[k]
                    request.path_variables = path_variables

                    try:
                        handler(request, response)
                    except:
                        response = HttpResponse()
                        self._error_handler(request, response)

                    response.send(sout)
        finally:
            s.close()

    # listener of the http messages, supporting multi-clients
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

    def route(
            self,
            _path: str | list[str] | tuple[str],
            method: HttpMethod,
            handler: Callable[[HttpRequest, HttpResponse], None],
    ):
        if isinstance(_path, str):
            _path = path(_path)
        if isinstance(_path, list):
            _path = tuple(_path)

        routing = self._routing
        path_variables = {}
        for i in range(len(_path)):
            name = _path[i]
            if name.startswith('{') and name.endswith('}'):
                path_variables[i] = name[1:-1]
                name = '*'

            routing = routing.setdefault(name, {})

        routing = routing.setdefault((), {})
        routing[method] = {
            "handler": handler,
            "path_variables": path_variables,
        }

    def get(
            self,
            _path: str | list[str] | tuple[str],
            handler: Callable[[HttpRequest, HttpResponse], None],
    ):
        self.route(_path, HttpMethod.GET, handler)

    def post(
            self,
            _path: str | list[str] | tuple[str],
            handler: Callable[[HttpRequest, HttpResponse], None],
    ):
        self.route(_path, HttpMethod.POST, handler)

    def head(
            self,
            _path: str | list[str] | tuple[str],
            handler: Callable[[HttpRequest, HttpResponse], None],
    ):
        self.route(_path, HttpMethod.HEAD, handler)

    # Checking the '_route' dictionary to get corresponding handler. That is, checking for path first, then checking
    # the method name
    def get_route(self, _path: str | list[str] | tuple[str], method: HttpMethod):
        if isinstance(_path, str):
            _path = path(_path)
        if isinstance(_path, list):
            _path = tuple(_path)

        routing = self._routing
        for i in range(len(_path)):
            name = _path[i]
            if name in routing:
                routing = routing[name]
            elif '*' in routing:
                routing = routing['*']
            else:
                return None

        if () not in routing:
            return None
        routing = routing[()]

        if method not in routing:
            return None
        return routing[method]

    def set_default_handler(self, handler: Callable[[HttpRequest, HttpResponse], None]):
        self._default_handler = handler

    def set_error_handler(self, handler: Callable[[HttpRequest, HttpResponse], None]):
        self._error_handler = handler

    @staticmethod
    def welcome_handler(request: HttpRequest, response: HttpResponse):
        response.body = """
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
        """
        response.headers["Content-Type"] = "text/html"

    @staticmethod
    def default_handler(request: HttpRequest, response: HttpResponse):
        response.code = HttpStatus.NOT_FOUND
        response.body = """
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
        """
        response.headers["Content-Type"] = "text/html"

    @staticmethod
    def error_handler(request: HttpRequest, response: HttpResponse):
        response.code = HttpStatus.INTERNAL_SERVER_ERROR
        response.body = """
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
        """
        response.headers["Content-Type"] = "text/html"
