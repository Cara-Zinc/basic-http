import logging
import os

from HttpRequest import HttpRequest, HttpMethod
from HttpResponse import HttpResponse, HttpStatus
from authorization import authenticate


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
        response.code = HttpStatus.BAD_REQUEST
        return

    if not path_param.startswith(username):
        response.code = HttpStatus.FORBIDDEN
        response.body = f"{username} is not the same as {path_param}"
        return
    file_path = "data/" + path_param
    print("file_path: " + file_path)
    # file_path = os.path.normpath(user_base_path + path_param)
    if not os.path.exists(file_path):
        response.code = HttpStatus.NOT_FOUND
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
