from datetime import datetime
from app.extensions import db


class ChatMessage(db.Model):

    __tablename__ = "chat_messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("chat_conversations.id"),
        nullable=True
    )

    group_id = db.Column(
        db.Integer,
        db.ForeignKey("chat_groups.id"),
        nullable=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    message = db.Column(
        db.Text,
        nullable=True
    )

    file_url = db.Column(
        db.Text,
        nullable=True
    )

    file_name = db.Column(
        db.Text,
        nullable=True
    )

    file_size = db.Column(
        db.Integer,
        nullable=True
    )

    file_type = db.Column(
        db.String(120),
        nullable=True
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    deleted = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
