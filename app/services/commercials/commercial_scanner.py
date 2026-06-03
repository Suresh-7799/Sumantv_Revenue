from app.models.commercial_client import (
    CommercialClient
)

from app.models.commercial_result import (
    CommercialResult
)

from app.extensions import db


from .ad_matcher import (
    match_ad
)


def process_frames(

    frame_paths,

    channel_name,

    video_url,

    publish_date,

    views
):

    clients = (
        CommercialClient
        .query
        .all()
    )

    for frame in frame_paths:

        for client in clients:

            found = match_ad(

                frame,

                client
            )

            if not found:
                continue

            existing = (

                CommercialResult
                .query
                .filter_by(

                    video_url=
                    video_url,

                    ad_name=
                    client.ad_name
                )
                .first()
            )

            if existing:
                continue

            result = CommercialResult(

                ad_name=
                client.ad_name,

                ad_type=
                client.ad_type,

                channel_name=
                channel_name,

                video_url=
                video_url,

                publish_date=
                publish_date,

                views=
                views,

                client_name=
                client.client_name,

                client_acquisition=
                client.client_acquisition,

                source=
                "OCR"
            )

            db.session.add(
                result
            )

            db.session.commit()

            return True

    return False
