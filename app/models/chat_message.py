from datetime import datetime

from app.extensions import db


class ChatMessage(db.Model):

    __tablename__ = "chat_messages"


    # =========================
    # PRIMARY KEY
    # =========================

    id = db.Column(

        db.Integer,

        primary_key=True
    )


    # =========================
    # CONVERSATIONS
    # =========================

    conversation_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "chat_conversations.id",
            ondelete="CASCADE"
        ),

        nullable=True,

        index=True
    )


    # =========================
    # GROUP
    # =========================

    group_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "chat_groups.id",
            ondelete="CASCADE"
        ),

        nullable=True,

        index=True
    )


    # =========================
    # USERS
    # =========================

    sender_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),

        nullable=False,

        index=True
    )

    receiver_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),

        nullable=True,

        index=True
    )


    # =========================
    # MESSAGE
    # =========================

    message = db.Column(

        db.Text,

        nullable=True
    )


    # =========================
    # FILES
    # =========================

    file_url = db.Column(

        db.Text,

        nullable=True
    )

    file_name = db.Column(

        db.String(255),

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

    file_category = db.Column(

        db.String(50),

        nullable=True
    )


    # =========================
    # STATUS
    # =========================

    is_read = db.Column(

        db.Boolean,

        default=False,

        nullable=False
    )

    deleted = db.Column(

        db.Boolean,

        default=False,

        nullable=False
    )


    # =========================
    # TIMESTAMPS
    # =========================

    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow,

        nullable=False,

        index=True
    )

    updated_at = db.Column(

        db.DateTime,

        default=datetime.utcnow,

        onupdate=datetime.utcnow,

        nullable=False
    )


    # =========================
    # RELATIONSHIPS
    # =========================

    sender = db.relationship(

        "User",

        foreign_keys=[sender_id],

        lazy=True
    )

    receiver = db.relationship(

        "User",

        foreign_keys=[receiver_id],

        lazy=True
    )


    # =========================
    # SERIALIZE
    # =========================

    def to_dict(self):

        return {

            "id":
            self.id,

            "conversation_id":
            self.conversation_id,

            "group_id":
            self.group_id,

            "sender_id":
            self.sender_id,

            "receiver_id":
            self.receiver_id,

            "message":
            self.message,

            "file_url":
            self.file_url,

            "file_name":
            self.file_name,

            "file_size":
            self.file_size,

            "file_type":
            self.file_type,

            "file_category":
            self.file_category,

            "is_read":
            self.is_read,

            "deleted":
            self.deleted,

            "created_at":
            self.created_at.isoformat()
            if self.created_at else None
        }
