from datetime import datetime

from app.models.youtube_channel import (
    YoutubeChannel
)

from app.dashboard.routes import (
    background_scan
)


def scan_all_channels(app):

    channels = (
        YoutubeChannel.query
        .filter_by(
            is_active=True
        )
        .all()
    )

    for channel in channels:

        try:

            background_scan(

                app,

                channel.id,

                "2020-01-01",

                datetime.now().strftime(
                    "%Y-%m-%d"
                )
            )

        except Exception as error:

            print(error)
