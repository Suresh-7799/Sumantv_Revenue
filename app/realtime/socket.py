from datetime import datetime

from flask_socketio import (

    emit,

    join_room
)

from flask_login import (

    current_user
)

from app.extensions import (

    socketio,

    db
)

from app.models.chat_message import (

    ChatMessage
)


@socketio.on("join")

def handle_join():

    join_room(
        str(current_user.id)
    )


@socketio.on("send_message")

def handle_send_message(data):

    receiver_id = int(
        data["receiver_id"]
    )

    message = data["message"].strip()

    if not message:

        return

    new_message = ChatMessage(

        sender_id=current_user.id,

        receiver_id=receiver_id,

        message=message,

        created_at=datetime.now()
    )

    db.session.add(
        new_message
    )

    db.session.commit()

    from datetime import datetime

    payload = {

        "id":
        new_message.id,

        "sender_id":
        current_user.id,

        "receiver_id":
        receiver_id,

        "message":
        message,

        "created_at":
        datetime.now().strftime(
            "%I:%M %p"
        )
    }

    emit(

        "receive_message",

        payload,

        room=str(receiver_id)
    )

    emit(

        "receive_message",

        payload,

        room=str(current_user.id)
    )