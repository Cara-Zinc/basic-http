import mimetypes
import os

from HttpRequest import HttpRequest
from HttpResponse import HttpResponse, HttpStatus
from HttpServer import HttpServer
from authorization import authenticate

def send_chunked_response(file_path, response):
    response.body = b''
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(8192)  # Read in 32 byte chunks
            if not chunk:
                break
            # Write the chunk size in hexadecimal + CRLF
            response.body += f"{len(chunk):X}\r\n".encode()
            # Write the chunk data itself + CRLF
            response.body += chunk + b"\r\n"

        response.body += b"0\r\n\r\n"

def build_boundary():
    import uuid
    return uuid.uuid4().hex

def handle_range_request(file_path, range_header, response):
    size = os.path.getsize(file_path)
    # Parse the Range header which may contain multiple byte-ranges
    ranges = range_header.replace('bytes=', '').split(',')
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    # Create a unique boundary for separating parts of the content
    boundary = build_boundary()

    response.code = HttpStatus.PARTIAL_CONTENT
    response.headers["Content-Type"] = f"multipart/byteranges; boundary={boundary}"
    response.body = b''

    for byte_range in ranges:
        start, end = byte_range.split('-')
        start = int(start) if start else 0
        end = int(end) if end else size - 1

        if start > end or end >= size:
            response.code = HttpStatus.RANGE_NOT_SATISFIABLE
            return

        response.body += f"--{boundary}\r\n".encode()
        response.body += f"Content-Type: {content_type}\r\n".encode()
        response.body += f"Content-Range: bytes {start}-{end}/{size}\r\n\r\n".encode()

        with open(file_path, "rb") as file:
            file.seek(start)
            response.body += file.read(end - start + 1)
            response.body += b"\r\n"

    response.body += f"--{boundary}--\r\n".encode()

    response.headers["Content-Length"] = str(len(response.body))