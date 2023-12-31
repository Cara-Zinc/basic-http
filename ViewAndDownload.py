import logging

import ByteRanges
from ChunkAndRange import *


def view_download_handler(request: HttpRequest, response: HttpResponse):
    access_path = os.path.join('data', *request.path)

    full_path = os.path.normpath(access_path)
    print(access_path, full_path)
    if ".." in request.path:
        response.code = HttpStatus.FORBIDDEN
        return

    if os.path.isfile(access_path):
        range_header = request.headers.get("Range")
        if range_header:
            handle_range_request(full_path, range_header, response)
            return

        is_chunked = request.parameters.get("chunked") == "1"
        if is_chunked:
            response.headers["Transfer-Encoding"] = "chunked"
            send_chunked_response(full_path, response)

        else:
            with open(full_path, "rb") as file:
                response.body = file.read()
        content_type, encoding = mimetypes.guess_type(full_path)

        response.headers["Content-Type"] = content_type
        response.headers["Content-Length"] = len(response.body)
        response.headers["Content-Disposition"] = f'attachment; filename="{os.path.basename(full_path)}"'

    elif os.path.isdir(access_path):
        # If the requested path is a directory, respond based on the query parameter SUSTech-HTTP
        sustech_http = request.parameters.get("SUSTech-HTTP", "0")
        if sustech_http == "1":
            # Response with list of files under the requested directory
            file_list = os.listdir(full_path)
            response.body = file_list
        else:
            # Response with HTML page
            print("access_path: " + access_path)
            directory_tree_display(request, response, access_path)

    else:
        HttpServer.default_handler(request, response)


def directory_tree_display(
        request: HttpRequest, response: HttpResponse, full_path: str
):
    # generate HTML page for directory view with file tree
    file_tree_html = generate_file_tree_html(full_path)
    upload_form_html = generate_upload_form_html(request.path)
    create_folder_form_html = generate_create_folder_form_html(request.path)
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
                <hr>
                {create_folder_form_html}
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


def generate_create_folder_form_html(path: list[str]) -> str:
    # generate HTML form for file upload
    directory_path = "/".join(path)
    return f"""
        <form action="http://localhost:8080/create_folder?path=/{directory_path}/" method="post">
            <input name="name" required>
            <input type="submit" value="Create Folder">
        </form>
    """


def generate_file_tree_html(directory_path: str) -> str:
    # generate HTML file tree for a directory
    logging.info(directory_path)
    file_tree_html = []

    for file in os.listdir(directory_path):
        full = os.path.join(directory_path, file)
        link = os.path.relpath(full, 'data')
        file_tree_html.append(
            f'<li><a href="/{link}">{file}</a>| {generate_delete_button_html(link)}</li>'
        )
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
