from flask_socketio import emit

from app.extensions import (
    socketio
)


@socketio.on("connect")
def handle_connect():

    emit(
        "connected",
        {
            "message":
            "Realtime connection established"
        }
    )


@socketio.on("disconnect")
def handle_disconnect():

    print(
        "[SOCKET DISCONNECTED]"
    )


def broadcast_notification(data):

    socketio.emit(

        "notification",

        data

    )