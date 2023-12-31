import base64

from HttpRequest import HttpRequest
from HttpResponse import HttpResponse, HttpStatus

# TODO: This should be replaced with a proper user management system, adding config files or other implementations

user_pass_table = {
    "user": "pass",
    "114514": "114514",
    "client1":"123",
    "client2":"123",
    "client3":"123",
}

def check_qualification(encoded_qualification):
    decoded_qualification = base64.b64decode(encoded_qualification).decode()
    username, password = decoded_qualification.split(":", 1)
    return user_pass_table.get(username) == password


def authenticate(request: HttpRequest, response: HttpResponse):
    
    auth_header = request.headers.get("Authorization")
    if auth_header is None or not auth_header.startswith("Basic "):
        response.code = HttpStatus.UNAUTHORIZED
        response.headers["WWW-Authenticate"] = 'Basic realm="Authorization Required"'
        return False, None

    encoded_info = auth_header.split(" ")[1]
    if not check_qualification(encoded_info):
        response.code = HttpStatus.UNAUTHORIZED
        response.body = """
            <html lang="en-us">
                <head>
                    <title>401 Unauthorized</title>
                </head>
                <body>
                    <h1>401 Not Unauthorized</h1>
                    <hr />
                    <p>
                        You need to provide valid user information before conducting more operations.
                    </p>
                </body>
            </html>
        """
        response.headers["Content-Type"] = "text/html"
        return False, None
    
    else:
        decoded_qualification = base64.b64decode(encoded_info).decode()
        username, _ = decoded_qualification.split(":",1)
    return True, username


def unauthorize_handler(response):
    response.code = HttpStatus.FORBIDDEN
    response.body = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Access Denied</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    background-color: #f2f2f2;
                    text-align: center;
                    padding: 50px;
                }
                .container {
                    background-color: white;
                    margin: auto;
                    width: 50%;
                    border: 3px solid #f1f1f1;
                    padding: 20px;
                }
                h1 {
                    color: #ff6666;
                }
                p {
                    color: #404040;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Access Denied</h1>
                <p>Sorry, you do not have permission to access this directory.</p>
            </div>
        </body>
        </html>
        """
    response.headers["Content-Type"] = "text/html"
