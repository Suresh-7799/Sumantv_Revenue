import os
import uuid
import mimetypes

from flask import current_app

from werkzeug.utils import secure_filename


# =========================
# CONFIG
# =========================

MAX_FILE_SIZE = 30 * 1024 * 1024


# =========================
# ALLOWED EXTENSIONS
# =========================

ALLOWED_EXTENSIONS = {

    # IMAGES

    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",

    # VIDEOS

    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm",

    # DOCUMENTS

    "pdf",

    "doc",
    "docx",

    "xls",
    "xlsx",

    "ppt",
    "pptx",

    # ARCHIVES

    "zip",
    "rar",
    "7z",

    # TEXT / CODE

    "txt",
    "json",
    "js",
    "py",
    "html",
    "css",
    "md"
}


# =========================
# FILE CHECK
# =========================

def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =========================
# FILE TYPE CATEGORY
# =========================

def get_file_category(extension):

    image_types = {

        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp"
    }

    video_types = {

        "mp4",
        "mov",
        "avi",
        "mkv",
        "webm"
    }

    if extension in image_types:
        return "image"

    if extension in video_types:
        return "video"

    return "file"


# =========================
# SAVE FILE
# =========================

def save_chat_file(file):

    if not file:

        raise ValueError(
            "No file uploaded"
        )

    original_name = secure_filename(
        file.filename or ""
    )

    if not original_name:

        raise ValueError(
            "Invalid filename"
        )

    if len(original_name) > 180:

        raise ValueError(
            "Filename too long"
        )

    if not allowed_file(original_name):

        raise ValueError(
            "Invalid file type"
        )

    # =========================
    # FILE SIZE
    # =========================

    file.seek(0, os.SEEK_END)

    size = file.tell()

    file.seek(0)

    if size > MAX_FILE_SIZE:

        raise ValueError(
            "Max upload size is 30MB"
        )

    # =========================
    # EXTENSION
    # =========================

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    # =========================
    # MIME CHECK
    # =========================

    mime_type = mimetypes.guess_type(
        original_name
    )[0]

    if not mime_type:

        mime_type = "application/octet-stream"

    # =========================
    # UNIQUE FILE NAME
    # =========================

    unique_name = (

        f"{uuid.uuid4().hex}.{extension}"
    )

    # =========================
    # UPLOAD PATH
    # =========================

    upload_folder = os.path.join(

        current_app.static_folder,

        "uploads",

        "chat"
    )

    os.makedirs(

        upload_folder,

        exist_ok=True
    )

    file_path = os.path.join(

        upload_folder,

        unique_name
    )

    # =========================
    # SAVE
    # =========================

    file.save(file_path)

    # =========================
    # RESPONSE
    # =========================

    return {

        "url":
        f"/static/uploads/chat/{unique_name}",

        "name":
        original_name,

        "size":
        size,

        "type":
        extension,

        "mime":
        mime_type,

        "category":
        get_file_category(
            extension
        )
    }
