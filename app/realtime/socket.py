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


@socketio.on("connect")

def handle_connect():

    print("SOCKET CONNECTED")

    if not current_user.is_authenticated:

        print("USER NOT AUTHENTICATED")

        return False

    print(f"CONNECTED USER: {current_user.id}")


@socketio.on("join")

def handle_join():

    if not current_user.is_authenticated:

        print("JOIN FAILED")

        return

    room = str(current_user.id)

    join_room(room)

    print(f"JOINED ROOM: {room}")


@socketio.on("send_message")

def handle_send_message(data):

    print("SEND EVENT HIT")

    print(data)

    if not current_user.is_authenticated:

        print("USER AUTH FAILED")

        return

    receiver_id = int(
        data["receiver_id"]
    )

    message = data["message"].strip()

    if not message:

        return

    try:

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

        print("MESSAGE SAVED")

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
            new_message.created_at.strftime(
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

        print("MESSAGE EMITTED")

    except Exception as e:

        print("CHAT ERROR:", str(e))

        db.session.rollback()