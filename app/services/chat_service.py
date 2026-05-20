import os
import uuid

from flask import current_app

from werkzeug.utils import secure_filename


MAX_FILE_SIZE = 30 * 1024 * 1024


ALLOWED_EXTENSIONS = {

    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",

    "mp4",
    "mov",
    "avi",
    "mkv",

    "pdf",

    "doc",
    "docx",

    "xls",
    "xlsx",

    "ppt",
    "pptx",

    "zip",
    "rar",
    "7z",

    "txt",
    "json",
    "js",
    "py",
    "html",
    "css",
    "md"
}


def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(
            ".",
            1
        )[1].lower()

        in ALLOWED_EXTENSIONS
    )


def save_chat_file(file):

    if not file:

        raise ValueError(
            "No file"
        )

    filename = secure_filename(
        file.filename
    )

    if not allowed_file(filename):

        raise ValueError(
            "Invalid file type"
        )

    file.seek(0, os.SEEK_END)

    size = file.tell()

    file.seek(0)

    if size > MAX_FILE_SIZE:

        raise ValueError(
            "Max upload size is 30MB"
        )

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    unique_name = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    upload_folder = os.path.join(

        current_app.static_folder,

        "uploads",

        "chat"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    path = os.path.join(
        upload_folder,
        unique_name
    )

    file.save(path)

    return {

        "url":
        f"/static/uploads/chat/{unique_name}",

        "name":
        filename,

        "size":
        size,

        "type":
        extension
    }
