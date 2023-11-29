import logging
import socket
import threading

from HttpRequest import HttpRequest
from HttpResponse import HttpResponse


class HttpServer:

    def __init__(self):
        self._server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __handler(self, s: socket.socket, addr: str):
        with s.makefile('rb', encoding='utf-8') as sin, s.makefile('wb', encoding='utf-8') as sout:
            for request in HttpRequest.receive_requests(sin):
                logging.debug(request)
                res = HttpResponse()
                res.body = {'message': 'Hello, world!'}
                res.send(sout)

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
