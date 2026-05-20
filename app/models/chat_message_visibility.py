from app.extensions import db


class ChatMessageVisibility(db.Model):

    __tablename__ = "chat_message_visibility"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey("chat_messages.id"),
        nullable=False
    )

    hidden_for_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
