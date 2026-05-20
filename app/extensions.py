from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import os

db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

bcrypt = Bcrypt()

mail = Mail()

csrf = CSRFProtect()

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading",
    manage_session=False,
    ping_timeout=60,
    ping_interval=25,
    logger=False,
    engineio_logger=False
)

limiter = Limiter(

    key_func=get_remote_address,

    storage_uri=os.getenv(
        "REDIS_URL"
    )
)

redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True
)
