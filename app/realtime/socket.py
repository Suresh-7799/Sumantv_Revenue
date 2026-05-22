from datetime import datetime

from zoneinfo import ZoneInfo


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

from app.models.chat_block import (
    ChatBlock
)

from app.models.chat_message_visibility import (
    ChatMessageVisibility


)

from app.models.chat_message import (
    ChatMessage
)

from app.models.chat_block import (
    ChatBlock
)

from app.models.chat_message_visibility import (
    ChatMessageVisibility
)


# =========================
# ONLINE USERS
# =========================

online_users = set()


# =========================
# ROOM BUILDER
# =========================

def build_room(user1, user2):

    ids = sorted([user1, user2])

    return f"chat_{ids[0]}_{ids[1]}"


# =========================
# TIMESTAMP FORMAT
# =========================

def format_timestamp(dt):

    local_dt = dt.astimezone(
        ZoneInfo("Asia/Kolkata")
    )

    now = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    if local_dt.date() == now.date():

        return local_dt.strftime(
            "%I:%M %p"
        )

    return local_dt.strftime(
        "%d %b %Y"
    )



# =========================
# ONLINE USERS
# =========================

online_users = set()


# =========================
# ROOM BUILDER
# =========================

def build_room(user1, user2):

    ids = sorted([user1, user2])

    return f"chat_{ids[0]}_{ids[1]}"


# =========================
# TIMESTAMP FORMAT
# =========================

def format_timestamp(dt):

    now = datetime.utcnow()

    if dt.date() == now.date():

        return dt.strftime("%I:%M %p")

    return dt.strftime("%d %b %Y")


# =========================
# CONNECT
# =========================

@socketio.on("send_message")
def handle_send_message(data):

    print("MESSAGE RECEIVED:", data)

    if current_user.is_authenticated:

        join_room(

            f"user_{current_user.id}"
        )

        online_users.add(
            current_user.id
        )


# =========================
# JOIN CHAT
# =========================

@socketio.on("join_chat")
def join_chat(data):

    if not current_user.is_authenticated:
        return

    try:

        receiver_id = int(
            data["receiver_id"]
        )

    except Exception:

        return

    room = build_room(

        current_user.id,

        receiver_id
    )

    join_room(room)

    emit(


        "receive_message",

        data,

        room=f"user_{data['receiver_id']}"
    )

    emit(

        "receive_message",

        data,

        room=f"user_{current_user.id}"
    )


# =========================
# JOIN CHAT
# =========================

@socketio.on("join_chat")
def join_chat(data):

    if not current_user.is_authenticated:
        return

    try:

        receiver_id = int(
            data["receiver_id"]
        )

    except Exception:

        return

    room = build_room(

        current_user.id,

        receiver_id
    )

    join_room(room)

    emit(



        "joined_chat",

        {
            "room":
            room
        }
    )


# =========================
# LEAVE CHAT
# =========================

@socketio.on("leave_chat")
def leave_chat(data):

    if not current_user.is_authenticated:
        return

    try:

        receiver_id = int(
            data["receiver_id"]
        )

    except Exception:

        return

    room = build_room(

        current_user.id,

        receiver_id
    )

    leave_room(room)


# =========================
# SEND MESSAGE
# =========================

@socketio.on("send_message")
def handle_send_message(data):

    if not current_user.is_authenticated:
        return

    try:

        receiver_id = int(
            data["receiver_id"]
        )

    except Exception:

        return

    blocked = ChatBlock.query.filter(

        (

            (
                ChatBlock.blocker_id
                ==
                current_user.id
            )

            &

            (
                ChatBlock.blocked_id
                ==
                receiver_id
            )

        )

        |

        (

            (
                ChatBlock.blocker_id
                ==
                receiver_id
            )

            &

            (
                ChatBlock.blocked_id
                ==
                current_user.id
            )

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

    if not isinstance(file_data, dict):

        file_data = None

    if not message and not file_data:

        return

    new_message = ChatMessage(

        sender_id=current_user.id,

        receiver_id=receiver_id,

        message=message,

        file_url=file_data.get("url")
        if file_data else None,

        file_name=file_data.get("name")
        if file_data else None,

        file_type=file_data.get("type")
        if file_data else None,

        file_size=file_data.get("size")
        if file_data else None,

        file_category=file_data.get("category")
        if file_data else None
    )

    db.session.add(
        new_message
    )

    db.session.commit()

    payload = {

        "id":
        new_message.id,

        "sender_id":
        current_user.id,

        "receiver_id":
        receiver_id,

        "message":
        new_message.message,

        "file_url":
        new_message.file_url,

        "file_name":
        new_message.file_name,

        "file_type":
        new_message.file_type,

        "file_size":
        new_message.file_size,

        "file_category":
        new_message.file_category,

        "created_at":
        format_timestamp(
            new_message.created_at
        ),

        "deleted":
        False,

        "is_read":
        False
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

# =========================
# DELETE MESSAGE
# =========================

@socketio.on("delete_message")
def delete_message(data):

    if not current_user.is_authenticated:
        return

    try:

        message_id = int(
            data["message_id"]
        )

    except Exception:

        return

    message = db.session.get(

        ChatMessage,

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
            "message_id":
            message_id
        },

        room=room
    )


# =========================
# CLEAR CHAT
# =========================

@socketio.on("clear_chat")
def clear_chat(data):

    if not current_user.is_authenticated:
        return

    try:

        receiver_id = int(
            data["receiver_id"]
        )

    except Exception:

        return

    messages = ChatMessage.query.filter(

        (

            (
                ChatMessage.sender_id
                ==
                current_user.id
            )

            &

            (
                ChatMessage.receiver_id
                ==
                receiver_id
            )

        )

        |

        (

            (
                ChatMessage.sender_id
                ==
                receiver_id
            )

            &

            (
                ChatMessage.receiver_id
                ==
                current_user.id
            )

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

        "chat_cleared",

        {

            "receiver_id":
            receiver_id
        },

        room=f"user_{current_user.id}"
    )


# =========================
# TYPING INDICATOR
# =========================

@socketio.on("typing")
def handle_typing(data):

    if not current_user.is_authenticated:
        return

    try:

        receiver_id = int(
            data["receiver_id"]
        )

    except Exception:

        return

    room = build_room(

        current_user.id,

        receiver_id
    )

    emit(

        "user_typing",

        {

            "user_id":
            current_user.id
        },

        room=room,

        include_self=False
    )


# =========================
# READ RECEIPTS
# =========================

@socketio.on("mark_read")
def mark_read(data):

    if not current_user.is_authenticated:
        return

    try:

        message_id = int(
            data["message_id"]
        )

    except Exception:

        return

    message = db.session.get(

        ChatMessage,

        message_id
    )

    if not message:
        return

    if message.receiver_id != current_user.id:
        return

    message.is_read = True

    db.session.commit()

    room = build_room(

        message.sender_id,

        message.receiver_id
    )

    emit(

        "message_read",

        {

            "message_id":
            message.id
        },

        room=room
    )


# =========================
# DISCONNECT
# =========================

@socketio.on("disconnect")
def handle_disconnect():

    if current_user.is_authenticated:

        online_users.discard(
            current_user.id
        )

        print(

            f"User disconnected: "
            f"{current_user.id}"
        )
