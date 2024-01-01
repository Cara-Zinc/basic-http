import logging
import os

from HttpRequest import HttpRequest, HttpMethod
from HttpResponse import HttpResponse, HttpStatus
from authorization import authenticate


def bad_request_handler(request: HttpRequest, response: HttpResponse):
    response.code = HttpStatus.BAD_REQUEST
    title = "Bad Request"
    message = "The specified path is not a file"
    response.body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding-top: 50px;
            }}
            .container {{
                background-color: #fff;
                margin: auto;
                width: 80%;
                max-width: 700px;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #5f9ea0;
            }}
            p {{
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            <p>{message}</p>
        </div>
    </body>
    </html>
    """
    response.headers["Content-Type"] = "text/html"


def delete_success_handler(request: HttpRequest, response: HttpResponse):
    response.body = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Success - File Deleted</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #e7f9f7;
                        color: #32a852;
                        text-align: center;
                        padding-top: 50px;
                    }
                    .container {
                        background-color: #fff;
                        margin: auto;
                        width: 60%;
                        padding: 40px;
                        border: 1px solid #32a852;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(50, 168, 82, 0.2);
                    }
                    h1 {
                        margin-bottom: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>File Deleted Successfully</h1>
                    <p>The file has been successfully removed from the server.</p>
                </div>
            </body>
        </html>
    """
    response.headers["Content-Type"] = "text/html"

def delete_handler(request: HttpRequest, response: HttpResponse):
    if request.method != HttpMethod.POST:
        response.code = HttpStatus.METHOD_NOT_ALLOWED
        return
    authorized, username = authenticate(request, response)
    if not authorized:
        response.code = HttpStatus.UNAUTHORIZED
        return

    path_param = request.parameters.get('path').removeprefix('/')
    if not path_param:
        bad_request_handler(request,response)
        return

    if not path_param.startswith(username):
        response.code = HttpStatus.FORBIDDEN
        response.body = f"{username} is not the same as {path_param}"
        return
    file_path = "data/" + path_param
    print("file_path: " + file_path)
    # file_path = os.path.normpath(user_base_path + path_param)
    if not os.path.exists(file_path):
        bad_request_handler(request,response)
        return

    response.code = HttpStatus.OK
    response.body = "File deleted successfully."
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            if len(os.listdir(file_path)) != 0:
                response.code = HttpStatus.BAD_REQUEST
                response.body = "The specified directory is not empty."
                return

            os.rmdir(file_path)
        else:
            response.code = HttpStatus.BAD_REQUEST
            response.body = "The specified path is not a file or directory."
    except OSError as e:
        response.code = HttpStatus.INTERNAL_SERVER_ERROR
        response.body = "An error occurred while deleting the file."
        logging.error(e)
