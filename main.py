import argparse
import signal

from ViewAndDownload import *
from delete import *
from upload import *


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '--inbound', '-i', default='0.0.0.0', help='inbound ip address')
    parser.add_argument('--port', '-p', type=int, default=8080, help='inbound port')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arg()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    logging.info(f'Will be listening on {args.host}:{args.port}')

    server = HttpServer()
    server.get("/", view_download_handler)
    server.get("/**", view_download_handler)
    server.post("/upload", upload_handler)
    server.post("/delete", delete_handler)
    server.post("/create_folder", create_folder_handler)
    # server.get("/var/*/{foo}/{bar}", test_path_variable)
    # server.get("/any/**", test_double_asterisk)
    # server.get("/range", test_range)
    server.listen(args.host, args.port)
