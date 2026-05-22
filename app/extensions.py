from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# =========================
# DATABASE
# =========================

db = SQLAlchemy()

migrate = Migrate()


# =========================
# LOGIN MANAGER
# =========================

login_manager = LoginManager()

login_manager.login_view = "auth.login"

login_manager.login_message_category = "warning"


# =========================
# SECURITY
# =========================

bcrypt = Bcrypt()

csrf = CSRFProtect()


# =========================
# MAIL
# =========================

mail = Mail()


# =========================
# SOCKET IO
# =========================

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading",
    manage_session=False,
    ping_timeout=120,
    ping_interval=25,
    logger=False,
    engineio_logger=False
)


# =========================
# RATE LIMITER
# =========================

limiter = Limiter(

    key_func=get_remote_address,

    storage_uri="memory://",

    default_limits=["5000 per day"]
)
