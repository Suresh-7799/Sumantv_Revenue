from datetime import datetime

from flask_socketio import (
    emit,
    join_room
)

from flask_login import current_user

from app.extensions import (
    socketio,
    db
)

from app.models.chat_group import (
    ChatGroup
)

from app.models.chat_group_member import (
    ChatGroupMember
)

from app.models.chat_message import (
    ChatMessage
)


# =========================
# GROUP ROOM
# =========================

def group_room(group_id):

    return f"group_{group_id}"


# =========================
# TIMESTAMP FORMAT
# =========================

def format_timestamp(dt):

    now = datetime.utcnow()

    if dt.date() == now.date():

        return dt.strftime("%I:%M %p")

    return dt.strftime("%d %b %Y")


# =========================
# JOIN GROUP
# =========================

@socketio.on("join_group")
def join_group(data):

    if not current_user.is_authenticated:
        return

    try:

        group_id = int(
            data["group_id"]
        )

    except Exception:

        emit(

            "chat_error",

            {
                "message":
                "Invalid group"
            }
        )

        return

    member = ChatGroupMember.query.filter_by(

        group_id=group_id,

        user_id=current_user.id

    ).first()

    if not member:

        emit(

            "chat_error",

            {
                "message":
                "Access denied"
            }
        )

        return

    join_room(
        group_room(group_id)
    )

    emit(

        "joined_group",

        {
            "group_id":
            group_id
        }
    )


# =========================
# GROUP MESSAGE
# =========================

@socketio.on("group_message")
def group_message(data):

    if not current_user.is_authenticated:
        return

    try:

        group_id = int(
            data["group_id"]
        )

    except Exception:

        emit(

            "chat_error",

            {
                "message":
                "Invalid group"
            }
        )

        return

    message = (
        data.get("message") or ""
    ).strip()

    if not message:

        return

    member = ChatGroupMember.query.filter_by(

        group_id=group_id,

        user_id=current_user.id

    ).first()

    if not member:

        emit(

            "chat_error",

            {
                "message":
                "Access denied"
            }
        )

        return

    new_message = ChatMessage(

        sender_id=current_user.id,

        group_id=group_id,

        message=message
    )

    db.session.add(
        new_message
    )

    db.session.commit()

    payload = {

        "id":
        new_message.id,

        "group_id":
        group_id,

        "sender_id":
        current_user.id,

        "message":
        new_message.message,

        "created_at":
        format_timestamp(
            new_message.created_at
        )
    }

    emit(

        "receive_group_message",

        payload,

        room=group_room(group_id)
    )