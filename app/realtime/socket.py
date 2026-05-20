from datetime import datetime

from app.models.chat_block import ChatBlock

from flask_socketio import (
    emit,
    join_room,
    leave_room
)

from flask_login import current_user

from app.extensions import (
    socketio,
    db
)

from app.models.chat_message import (
    ChatMessage
)


def build_room(user1, user2):

    ids = sorted([user1, user2])

    return f"chat_{ids[0]}_{ids[1]}"


def format_timestamp(dt):

    now = datetime.utcnow()

    if dt.date() == now.date():

        return dt.strftime("%I:%M %p")

    return dt.strftime("%d %b %Y")


@socketio.on("connect")
def handle_connect():

    if not current_user.is_authenticated:
        return False

    join_room(f"user_{current_user.id}")


@socketio.on("join_chat")
def join_chat(data):

    receiver_id = int(data["receiver_id"])

    room = build_room(
        current_user.id,
        receiver_id
    )

    join_room(room)

    emit(
        "joined_chat",
        {
            "room": room
        }
    )


@socketio.on("leave_chat")
def leave_chat(data):

    receiver_id = int(data["receiver_id"])

    room = build_room(
        current_user.id,
        receiver_id
    )

    leave_room(room)


@socketio.on("send_message")
def handle_send_message(data):

    receiver_id = int(
        data["receiver_id"]
    )

    blocked = ChatBlock.query.filter(

        (
            (ChatBlock.blocker_id == current_user.id)
            &
            (ChatBlock.blocked_id == receiver_id)
        )

        |

        (
            (ChatBlock.blocker_id == receiver_id)
            &
            (ChatBlock.blocked_id == current_user.id)
        )

    ).first()

    if blocked:

        emit(
            "chat_error",
            {
                "message":
                "User unavailable"
            }
        )

        return

    message = (
        data.get("message") or ""
    ).strip()

    file_data = data.get("file")

    if not message and not file_data:
        return

    new_message = ChatMessage(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        message=message,
        file_url=file_data.get("url") if file_data else None,
        file_name=file_data.get("name") if file_data else None,
        file_type=file_data.get("type") if file_data else None
    )

    db.session.add(new_message)

    db.session.commit()

    payload = {
        "id": new_message.id,
        "sender_id": current_user.id,
        "receiver_id": receiver_id,
        "message": new_message.message,
        "file_url": new_message.file_url,
        "file_name": new_message.file_name,
        "file_type": new_message.file_type,
        "created_at":
        format_timestamp(
            new_message.created_at
        )
    }

    room = build_room(
        current_user.id,
        receiver_id
    )

    emit(
        "receive_message",
        payload,
        room=room
    )


@socketio.on("delete_message")
def delete_message(data):

    message_id = int(data["message_id"])

    message = ChatMessage.query.get(
        message_id
    )

    if not message:
        return

    if message.sender_id != current_user.id:
        return

    message.deleted = True

    db.session.commit()

    room = build_room(
        message.sender_id,
        message.receiver_id
    )

    emit(
        "message_deleted",
        {
            "message_id": message_id
        },
        room=room
    )


@socketio.on("clear_chat")
def clear_chat(data):

    receiver_id = int(
        data["receiver_id"]
    )

    messages = ChatMessage.query.filter(

        (
            (ChatMessage.sender_id == current_user.id)
            &
            (ChatMessage.receiver_id == receiver_id)
        )

        |

        (
            (ChatMessage.sender_id == receiver_id)
            &
            (ChatMessage.receiver_id == current_user.id)
        )

    ).all()

    for msg in messages:

        exists = ChatMessageVisibility.query.filter_by(

            message_id=msg.id,

            hidden_for_user_id=current_user.id

        ).first()

        if exists:

            continue

        hidden = ChatMessageVisibility(

            message_id=msg.id,

            hidden_for_user_id=current_user.id
        )

        db.session.add(hidden)

    db.session.commit()

    emit(
        "chat_cleared"
    )