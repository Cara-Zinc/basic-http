import argparse

from HttpServer import HttpServer


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '--inbound', '-i', default='0.0.0.0', help='inbound ip address')
    parser.add_argument('--port', '-p', type=int, default=8080, help='inbound port')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arg()
    print(f'Will be listening on {args.host}:{args.port}')

    server = HttpServer()
    server.listen(args.host, args.port)
