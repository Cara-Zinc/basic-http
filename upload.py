import os
import cgi
import re
import logging
from HttpRequest import HttpRequest, HttpMethod
from HttpResponse import HttpResponse, HttpStatus
from HttpServer import HttpServer
from authorization import authenticate

def parse_multipart_body(body: bytes, boundary: str):
    # Split the body based on the boundary
    parts = body.split(b'--' + boundary.encode())
    print("how many parts: ")
    # print(len(parts))
    # print(parts)
    for part in parts:
        if not b'\r\n\r\n' in part:
            continue
        else:
            # Split headers and content
            headers, content = part.split(b'\r\n\r\n', 1)
            headers = re.split(';|\r\n',headers.decode())
            for i in range(len(headers)-1,-1,-1):
                if not "=" in headers[i] and not ":" in headers[i]:
                   del headers[i]

            header_dict = {k.strip(): v.strip() for k, v in (re.split(':|=',h) for h in headers)}
            filename = header_dict['filename']
            if filename:
                    print("name: "+filename)
                    # Return filename and content
                    yield filename, content.rstrip(b'\r\n--')
                 

def upload_handler(request: HttpRequest, response: HttpResponse):
    
    if request.method != HttpMethod.POST:
        response.code = HttpStatus.METHOD_NOT_ALLOWED
        return

    authorized, username = authenticate(request, response)
    if authorized:
        print("username: "+username)
    else:
        print("unauthorized")
    if not authorized:
        response.code = HttpStatus.UNAUTHORIZED
        return

    # Check if path parameter is provided
    path_param = request.parameters.get('path')
    if not path_param:
        response.code = HttpStatus.BAD_REQUEST
        return

    # Construct the user-specific base path and check permission
    user_base_path = f"{username}/"
    if not path_param.removeprefix('/').startswith(user_base_path):
        response.code = HttpStatus.FORBIDDEN
        return

    # Check if the target directory exists
    user_base_path = "data/"+path_param
    target_directory = os.path.join(user_base_path)
    # a test on directory analysis
    # print("target_directory: "+target_directory)
    

    if not os.path.exists(target_directory):
        response.code = HttpStatus.NOT_FOUND
        return

    # Handle file upload
    
    content_type = request.headers.get('Content-Type')
    if not content_type or 'multipart/form-data' not in content_type:
        response.code = HttpStatus.BAD_REQUEST
        return

    _, params = cgi.parse_header(content_type)
    
    boundary = params.get('boundary')
    if not boundary:
        response.code = HttpStatus.BAD_REQUEST
        return
    # print("boundary: "+boundary)
    for filename, file_content in parse_multipart_body(request.body, boundary):
        filename = filename.replace('"','')
        file_path = os.path.join(target_directory, filename)
        # print(file_path)
        # print(filename)
        try:
            with open(file_path, 'wb') as file:
                file.write(file_content)
        except Exception as e:
            logging.exception(e)
            response.code = HttpStatus.INTERNAL_SERVER_ERROR
            return

    response.code = HttpStatus.OK
    response.body = "Files uploaded successfully."
    response.headers["Content-Type"] = "text/html"
