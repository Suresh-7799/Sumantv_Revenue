import os

from werkzeug.utils import secure_filename


class UploadService:

    ALLOWED_EXTENSIONS = {
        "xlsx",
        "csv",
        "xls"
    }

    @staticmethod
    def allowed_file(filename):

        return (
            "." in filename
            and
            filename.rsplit(
                ".",
                1
            )[1].lower()
            in UploadService.ALLOWED_EXTENSIONS
        )

    @staticmethod
    def save_file(
        file,
        upload_folder
    ):

        if not file:

            raise ValueError(
                "No file provided"
            )

        if not UploadService.allowed_file(
            file.filename
        ):

            raise ValueError(
                "Invalid file type"
            )

        filename = secure_filename(
            file.filename
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        filepath = os.path.join(
            upload_folder,
            filename
        )

        file.save(filepath)

        return {

            "filename": filename,

            "path": filepath

        }