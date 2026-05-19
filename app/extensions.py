from flask_sqlalchemy import (
    SQLAlchemy
)

from flask_migrate import (
    Migrate
)

from flask_login import (
    LoginManager
)

from flask_bcrypt import (
    Bcrypt
)

from flask_mail import (
    Mail
)

from flask_wtf.csrf import (
    CSRFProtect
)

from flask_socketio import (
    SocketIO
)

from flask_limiter import (
    Limiter
)

from flask_limiter.util import (
    get_remote_address
)

import redis


db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

bcrypt = Bcrypt()

mail = Mail()

csrf = CSRFProtect()

socketio = SocketIO(

    cors_allowed_origins="*",

    async_mode="eventlet"

)

limiter = Limiter(

    key_func=get_remote_address

)


redis_client = redis.Redis(

    host="localhost",

    port=6379,

    decode_responses=True

)
