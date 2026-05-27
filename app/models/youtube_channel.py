from app.extensions import db


class YoutubeChannel(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    channel_name = db.Column(
        db.String(255),
        nullable=False
    )

    channel_url = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
