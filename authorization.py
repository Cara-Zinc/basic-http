import base64
from HttpRequest import HttpRequest
from HttpResponse import HttpResponse, HttpStatus
from HttpServer import HttpServer
# This should be replaced with a proper user management system
VALID_USERNAME = "user"
VALID_PASSWORD = "pass"
ENCODED_QUALIFICATION = base64.b64encode(f"{VALID_USERNAME}:{VALID_PASSWORD}".encode()).decode()

def check_qualification(encoded_qualification):
    return encoded_qualification == ENCODED_QUALIFICATION

def authenticate(request: HttpRequest, response: HttpResponse):
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Basic '):
        response.code = HttpStatus.UNAUTHORIZED
        response.headers['WWW-Authenticate'] = 'Basic realm="Authorization Required"'
        return False
    
    encoded_info = auth_header.split(' ')[1]
    if not check_qualification(encoded_info):
        response.code = HttpStatus.UNAUTHORIZED
        return False

    return True
