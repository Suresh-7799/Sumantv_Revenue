from app.extensions import db

class CommercialClient(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ad_name = db.Column(
        db.String(255),
        nullable=False
    )

    ad_type = db.Column(
        db.String(100)
    )

    client_name = db.Column(
        db.String(255)
    )

    client_acquisition = db.Column(
        db.String(255)
    )

    sample_images = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
