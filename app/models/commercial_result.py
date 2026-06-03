from app.extensions import db

class CommercialResult(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ad_name = db.Column(
        db.String(255)
    )

    ad_type = db.Column(
        db.String(100)
    )

    channel_name = db.Column(
        db.String(255)
    )

    video_url = db.Column(
        db.Text
    )

    views = db.Column(
        db.String(100)
    )

    publish_date = db.Column(
        db.String(50)
    )

    client_name = db.Column(
        db.String(255)
    )

    client_acquisition = db.Column(
        db.String(255)
    )

    source = db.Column(
        db.String(20)
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
