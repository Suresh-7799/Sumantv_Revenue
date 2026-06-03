import os

from yt_dlp import YoutubeDL


def download_video(
    video_url,
    output_folder
):

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    output_path = os.path.join(
        output_folder,
        "%(id)s.%(ext)s"
    )

    with YoutubeDL({

        "format":
        "mp4",

        "outtmpl":
        output_path,

        "quiet":
        True
    }) as ydl:

        info = ydl.extract_info(
            video_url,
            download=True
        )

        return ydl.prepare_filename(
            info
        )
