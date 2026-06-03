from datetime import datetime

from app.extensions import db


class YoutubeTracking(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    video_title = db.Column(
        db.String(500)
    )

    video_url = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    channel_name = db.Column(
        db.String(255)
    )

    strip_name = db.Column(
        db.String(255)
    )

    published_date = db.Column(
        db.String(20)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

