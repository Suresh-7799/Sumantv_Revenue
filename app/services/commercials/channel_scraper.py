from yt_dlp import YoutubeDL


def get_latest_videos(
    channel_url,
    limit=10
):

    ydl_opts = {
        "extract_flat": True,
        "quiet": True
    }

    with YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(
            channel_url,
            download=False
        )

    entries = info.get(
        "entries",
        []
    )

    results = []

    for video in entries[:limit]:

        results.append({

            "title":
            video.get(
                "title"
            ),

            "url":
            f"https://www.youtube.com/watch?v={video.get('id')}",

            "video_id":
            video.get(
                "id"
            )
        })

    return results
