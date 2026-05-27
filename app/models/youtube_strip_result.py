from app.extensions import db


class YoutubeStripResult(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    channel_name = db.Column(
        db.String(255)
    )

    video_title = db.Column(
        db.Text
    )

    video_url = db.Column(
        db.Text
    )

    strip_text = db.Column(
        db.Text
    )

    detected_time = db.Column(
        db.Integer
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
