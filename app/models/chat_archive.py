from datetime import datetime
from app.extensions import db


class ChatArchive(db.Model):

    __tablename__ = "chat_archives"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("chat_conversations.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
