import mimetypes
import os

import HttpRequest
import HttpResponse
from HttpServer import HttpServer


def view_download_handler(request: HttpRequest, response: HttpResponse):
    access_path = "/data" + "/".join(request.path)
    full_path = os.path.normpath(access_path)
    print(access_path, full_path)
    if os.path.isfile(full_path):
        # If the requested path is a file, respond with binary file content
        with open(full_path, "rb") as file:
            response.body = file.read()
        content_type, encoding = mimetypes.guess_type(full_path)
        response.headers["Content-Type"] = content_type
        response.headers["Content-Length"] = len(response.body)

    elif os.path.isdir(full_path):
        # If the requested path is a directory, respond based on the query parameter SUSTech-HTTP
        sustech_http = request.headers.get("SUSTech-HTTP", "0")

        if sustech_http == "0":
            # Response with HTML page
            directory_tree_display(request, response, full_path)
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

    response.body = f"""
        <html lang="en-us">
            <head>
                <title>Directory View</title>
            </head>
            <body>
                <h1>Directory View</h1>
                {file_tree_html}
            </body>
        </html>
        """
    response.headers["Content-Type"] = "text/html"
    response.headers["Content-Length"] = len(response.body)


def generate_file_tree_html(directory_path: str) -> str:
    # generate HTML file tree for a directory
    file_tree_html = []

    for root, dirs, files in os.walk(directory_path):
        relative_path = os.path.relpath(root, directory_path)
        file_tree_html.append(f"<ul><b>{relative_path}</b>")

        for file_name in files:
            file_path = os.path.join(relative_path, file_name)
            file_tree_html.append(f'<li><a href="{file_path}">{file_name}</a></li>')

        file_tree_html.append("</ul>")

    return "\n".join(file_tree_html)
