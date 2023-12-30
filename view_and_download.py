import mimetypes
import os

import ByteRanges
from HttpRequest import HttpRequest
from HttpResponse import HttpResponse, HttpStatus
from HttpServer import HttpServer
from authorization import authenticate



def view_download_handler(request: HttpRequest, response: HttpResponse):
    authorized, username = authenticate(request, response)
    if not authorized:
        return
    access_path = "data/" + "/".join(request.path)
    if request.path[0] != username:
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
        return

    
    full_path = os.path.normpath(access_path)
    print(access_path, full_path)
    if ".." in request.path:
        response.code = HttpStatus.FORBIDDEN
        return
    if os.path.isfile(access_path):
        # If the requested path is a file, respond with binary file content
        with open(full_path, "rb") as file:
            response.body = file.read()
        content_type, encoding = mimetypes.guess_type(full_path)
        response.headers["Content-Type"] = content_type
        response.headers["Content-Length"] = len(response.body)
        response.headers[
            "Content-Disposition"
        ] = f'attachment; filename="{os.path.basename(full_path)}"'

    elif os.path.isdir(access_path):
        # If the requested path is a directory, respond based on the query parameter SUSTech-HTTP
        sustech_http = request.parameters.get("SUSTech-HTTP", "0")
        if sustech_http == "0":
            # Response with HTML page
            print("access_path: " + access_path)
            directory_tree_display(request, response, access_path)
        elif sustech_http == "1":
            # Response with list of files under the requested directory
            file_list = os.listdir(full_path)
            response.body = "\n".join(file_list)
            response.headers["Content-Type"] = "text/plain"
            response.headers["Content-Length"] = len(response.body)
    else:
        HttpServer.default_handler(request, response)


def directory_tree_display(
    request: HttpRequest, response: HttpResponse, full_path: str
):
    # generate HTML page for directory view with file tree
    file_tree_html = generate_file_tree_html(full_path)
    upload_form_html = generate_upload_form_html(request.path)
    response.body = f"""
        <html lang="en-us">
            <head>
                <title>Directory View</title>
            </head>
            <body>
                <h1>Directory View</h1>
                {file_tree_html}
                <hr>
                {upload_form_html}
            </body>
        </html>
        """
    response.headers["Content-Type"] = "text/html"
    response.headers["Content-Length"] = len(response.body)

def generate_upload_form_html(path: list[str]) -> str:
    # generate HTML form for file upload
    directory_path = "/".join(path)
    return f"""
        <form action="http://localhost:8080/upload?path=/{directory_path}/" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="Upload">
        </form>
    """

def generate_file_tree_html(directory_path: str) -> str:
    # generate HTML file tree for a directory
    file_tree_html = []
    prefix_path = ""
    if not directory_path.endswith("/"):
        index = directory_path.rfind("/")
        prefix_path = directory_path[index + 1 :]
    print("prefix_path: "+prefix_path)
    for root, dirs, files in os.walk(directory_path):
        relative_path = os.path.relpath(root, directory_path)
        if files:
            file_tree_html.append(f"<b>file</b>")
        for file_name in files:
            file_path = os.path.join(relative_path, file_name).removeprefix(".")
            full_file_path = f'/{prefix_path}{file_path}'
            file_tree_html.append(
                f'<li><a href="/{prefix_path}{file_path}">{file_name}</a>| {generate_delete_button_html(full_file_path)}</li>'
            )
        if dirs:
            file_tree_html.append(f"<b>directory</b>")
        for dir_name in dirs:
            dir_path = os.path.join(relative_path,  dir_name)
            file_tree_html.append(
                f'<li><a href="/{prefix_path}{dir_path}">{dir_name}</a></li>'
            )
        break
    return "\n".join(file_tree_html)

def generate_delete_button_html(file_path: str) -> str:
    return f"""
        <form action="http://localhost:8080/delete?path={file_path}" method="post" style="display: inline;">
            <input type="submit" value="Delete" onclick="return confirm('Are you sure you want to delete this file?');">
        </form>
    """

def test_path_variable(request: HttpRequest, response: HttpResponse):
    response.body = request.path_variables


def test_double_asterisk(request: HttpRequest, response: HttpResponse):
    response.body = request.path


def test_range(request: HttpRequest, response: HttpResponse):
    b = ByteRanges.ByteRanges(1024)
    b.append('114514\r\n1919810', 0)
    b.append({'foo': 'bar'}, 1010)
    response.body = b
