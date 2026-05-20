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


def group_room(group_id):

    return f"group_{group_id}"


@socketio.on("join_group")
def join_group(data):

    group_id = int(
        data["group_id"]
    )

    member = ChatGroupMember.query.filter_by(

        group_id=group_id,

        user_id=current_user.id

    ).first()

    if not member:

        return

    join_room(
        group_room(group_id)
    )


@socketio.on("group_message")
def group_message(data):

    group_id = int(
        data["group_id"]
    )

    message = (
        data.get("message") or ""
    ).strip()

    member = ChatGroupMember.query.filter_by(

        group_id=group_id,

        user_id=current_user.id

    ).first()

    if not member:

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

    emit(

        "receive_group_message",

        {

            "id":
            new_message.id,

            "group_id":
            group_id,

            "sender_id":
            current_user.id,

            "message":
            message,

            "created_at":
            new_message.created_at.strftime(
                "%I:%M %p"
            )
        },

        room=group_room(group_id)
    )