import os
import logging
from authorization import authenticate
from HttpRequest import HttpRequest, HttpMethod
from HttpResponse import HttpResponse,HttpStatus


def delete_handler(request: HttpRequest, response: HttpResponse):
    if request.method != HttpMethod.POST:
        response.code = HttpStatus.METHOD_NOT_ALLOWED
        return
    authorized, username = authenticate(request, response)
    if not authorized:
        response.code = HttpStatus.UNAUTHORIZED
        return

    path_param = request.parameters.get('path')
    if not path_param:
        response.code = HttpStatus.BAD_REQUEST
        return

    user_base_path = f"/{username}"
    if not path_param.startswith(user_base_path):
        response.code = HttpStatus.FORBIDDEN
        response.body = f"{user_base_path} is not the same as {path_param}"
        return
    file_path = "data/"+path_param
    print("file_path: "+file_path)
    # file_path = os.path.normpath(user_base_path + path_param)
    if not os.path.exists(file_path):
        response.code = HttpStatus.NOT_FOUND
        return

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            response.code = HttpStatus.OK
            response.body = "File deleted successfully."
            response.headers["Content-Type"] = "text/html"
        except Exception as e:
            logging.exception(e)
            response.code = HttpStatus.INTERNAL_SERVER_ERROR
    else:
        response.code = HttpStatus.BAD_REQUEST
        response.body = "The specified path is not a file."
        response.headers["Content-Type"] = "text/html"
