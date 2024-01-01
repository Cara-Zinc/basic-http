import logging

import ByteRanges
from ChunkAndRange import *


def view_download_handler(request: HttpRequest, response: HttpResponse):
    access_path = os.path.join('data', *request.path)

    authenticated, username = authenticate(request,response)
    
    if username:
        path_url = request.path[0]
        if authenticated and not path_url.startswith(username):
            authenticated = False

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
            directory_tree_display(request, response, access_path, authenticated)

    else:
        HttpServer.default_handler(request, response)

def head_handler(request: HttpRequest, response: HttpResponse):
    view_download_handler(request,response)
    response.body = ''

def directory_tree_display(
        request: HttpRequest, response: HttpResponse, full_path: str, authenticated: bool
):
    # generate HTML page for directory view with file tree
    file_tree_html = generate_file_tree_html(full_path, authenticated)
    upload_form_html = generate_upload_form_html(request.path)
    create_folder_form_html = generate_create_folder_form_html(request.path)
    upload_form_html = generate_upload_form_html(request.path) if authenticated else ""
    create_folder_form_html = generate_create_folder_form_html(request.path) if authenticated else ""

    response.body = f"""
        <html lang="en-us">
            <head>
                <title>Directory View</title>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                        color: #333;
                    }}
                    .container {{
                        width: 80%;
                        margin: auto;
                        padding: 20px;
                    }}
                    h1 {{
                        color: #5f9ea0;
                    }}
                    hr {{
                        border: 0;
                        height: 1px;
                        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));
                    }}
                    .form-container {{
                        margin-top: 20px;
                        text-align: center;
                    }}
                
                    .btn {{
                        background-color: #4CAF50; /* Green */
                        border: none;
                        color: white;
                        padding: 8px 16px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 14px;
                        margin: 4px 2px;
                        transition-duration: 0.4s;
                        cursor: pointer;
                    }}
                    
                    .btn:hover {{
                        background-color: white;
                        color: black;
                        border: 1px solid #4CAF50;
                    }}

                    .custom-file-upload {{
                        border: 1px solid #ccc;
                        display: inline-block;
                        padding: 6px 12px;
                        cursor: pointer;
                    }}
                    
                    .upload-form,
                    .create-folder-form {{
                        margin-bottom: 20px;
                    }}

                    .upload-form input[type="file"],
                    .create-folder-form input {{
                        margin-right: 10px;
                    }}
                    
                    .upload-form input[type="submit"],
                    .create-folder-form input[type="submit"] {{
                        visibility: hidden;
                    }}
                    .file-tree {{
                        list-style-type: none;
                        padding: 0;
                    }}

                    .file-tree li {{
                        padding: 8px;
                        margin: 8px 0;
                        background: #fff;
                        border-radius: 4px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    }}

                    .file-tree .file-name {{
                        flex-grow: 1;
                    }}

                    .btn.view-btn {{
                        background-color: #4CAF50;
                        /* ...other button styles... */
                    }}

                    .delete-form {{
                        display: inline;
                    }}

                    .btn.delete-btn {{
                        background-color: #f44336;
                        /* ...other button styles... */
                    }}

                </style>

            </head>
            <body>
                <div class="container">
                    <h1>Directory View</h1>
                    {file_tree_html}
                    {f'<div class="form-container">{upload_form_html}</div>' if authenticated else ''}
                    {f'<div class="form-container">{create_folder_form_html}</div>' if authenticated else ''}
                </div>
            </body>
        </html>
        """
    response.headers["Content-Type"] = "text/html"
    response.headers["Content-Length"] = len(response.body)


def generate_upload_form_html(path: list[str]) -> str:
    directory_path = "/".join(path)
    return f"""
        <div class="upload-form">
            <form action="http://localhost:8080/upload?path=/{directory_path}/" method="post" enctype="multipart/form-data">
                <label for="file-upload" class="custom-file-upload">
                    <i class="fa fa-cloud-upload"></i> Choose File
                </label>
                <input id="file-upload" type="file" name="file" required/>
                <button type="submit" class="btn">Upload</button>
            </form>
        </div>
    """

def generate_create_folder_form_html(path: list[str]) -> str:
    directory_path = "/".join(path)
    return f"""
        <div class="create-folder-form">
            <form action="http://localhost:8080/create_folder?path=/{directory_path}/" method="post">
                <input name="name" placeholder="New Folder Name" required/>
                <button type="submit" class="btn">Create Folder</button>
            </form>
        </div>
    """

def generate_file_tree_html(directory_path: str, authenticated: bool) -> str:
    # generate HTML file tree for a directory
    logging.info(directory_path)
    file_tree_html = ['<ul class="file-tree">']

    for file in os.listdir(directory_path):
        full = os.path.join(directory_path, file)
        link = os.path.relpath(full, 'data')
        delete_button = generate_delete_button_html(link) if authenticated else ''
        file_tree_html.append(
            f'<li class="file-item"><span class="file-name">{file}</span><div class="file-actions"><a href="/{link}" class="btn view-btn">Download</a>{delete_button}</div></li>'
        )
    return "\n".join(file_tree_html)


def generate_delete_button_html(file_path: str) -> str:
    return f"""
        <form action="http://localhost:8080/delete?path={file_path}" method="post" style="display: inline;">
            <input type="submit" class="btn delete-btn" value="Delete" onclick="return confirm('Are you sure you want to delete this file?');">
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
