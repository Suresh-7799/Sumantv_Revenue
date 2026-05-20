from datetime import datetime
from app.extensions import db


class ChatConversation(db.Model):

    __tablename__ = "chat_conversations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_one_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user_two_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
