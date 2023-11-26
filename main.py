import argparse
import socket
import threading


def handle_connection(connection, address):
    print(f"Connected from {addr}")


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '--inbound', '-i', default='0.0.0.0', help='inbound ip address')
    parser.add_argument('--port', '-p', type=int, default=8080, help='inbound port')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arg()
    print(f'Will be listening on {args.host}:{args.port}')

    ss = socket.socket()
    ss.bind((args.host, args.port))
    ss.listen()

    try:
        while True:
            s, addr = ss.accept()
            threading.Thread(target=handle_connection, args=(s, addr)).start()
    except KeyboardInterrupt:
        pass
    finally:
        ss.close()