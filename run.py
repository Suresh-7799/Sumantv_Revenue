from app import create_app

from app.extensions import (
    socketio
)


flask_app = create_app()


if __name__ == "__main__":

    socketio.run(
        flask_app,
        debug=True
    )
