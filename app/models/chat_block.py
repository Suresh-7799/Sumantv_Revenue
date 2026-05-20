from datetime import datetime
from app.extensions import db


class ChatBlock(db.Model):

    __tablename__ = "chat_blocks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    blocker_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    blocked_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
