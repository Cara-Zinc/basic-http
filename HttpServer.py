import socket
import threading


class HttpServer:

    def __init__(self):
        self._server_socket = socket.socket()

    def __handler(self, s: socket.socket, addr: str):
        pass

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
