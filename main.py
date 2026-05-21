import os

from app import create_app

from app.extensions import socketio


app = create_app()


if __name__ == "__main__":

<<<<<<< HEAD
    app = create_app()

=======
>>>>>>> 54e2499 (Updated all project files)
    socketio.run(

        app,

        host="0.0.0.0",

        port=5000,

        debug=False,

        allow_unsafe_werkzeug=True
    )
