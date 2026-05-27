from datetime import datetime

from app.extensions import db


class YoutubeTracking(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    link = db.Column(
        db.Text,
        nullable=False
    )

    channel_name = db.Column(
        db.String(255)
    )

    strip_name = db.Column(
        db.String(255)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )