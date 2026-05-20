from datetime import datetime
from app.extensions import db


class ChatGroupMember(db.Model):

    __tablename__ = "chat_group_members"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    group_id = db.Column(
        db.Integer,
        db.ForeignKey("chat_groups.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    joined_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
