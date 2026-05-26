from flask import Flask
from flask import render_template

from datetime import datetime, date

from app.config.settings import (
    DevelopmentConfig
)

from app.extensions import (

    db,

    migrate,

    login_manager,

    bcrypt,

    csrf,

    socketio,

    limiter
)

from app.utils.name_helper import (
    extract_display_name
)


def format_dob(value):

    if not value:

        return "-"

    # Python date/datetime object

    if isinstance(value, (datetime, date)):

        return value.strftime(
            "%d/%m/%Y"
        )

    # Legacy string values

    if isinstance(value, str):

        value = value.strip()

        if not value:

            return "-"

        formats = [

            "%Y-%m-%d",

            "%d/%m/%Y",

            "%Y/%m/%d"
        ]

        for fmt in formats:

            try:

                parsed = datetime.strptime(
                    value,
                    fmt
                )

                return parsed.strftime(
                    "%d/%m/%Y"
                )

            except ValueError:

                continue

        return value

    return "-"


def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.config.from_object(DevelopmentConfig)

    from app.models.chat_conversation import ChatConversation
    from app.models.chat_message import ChatMessage
    from app.models.chat_block import ChatBlock
    from app.models.chat_archive import ChatArchive
    from app.models.chat_message_visibility import ChatMessageVisibility
    from app.models.chat_group import ChatGroup
    from app.models.chat_group_member import ChatGroupMember

    initialize_extensions(app)

    configure_jinja(app)

    register_blueprints(app)

    @app.errorhandler(429)
    def ratelimit_error(error):

        return render_template(
            "errors/429.html"
        ), 429

    from app.realtime import socket
    from app.realtime import group_socket

    configure_login_manager()

    return app


def initialize_extensions(app):

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )

    login_manager.init_app(app)

    bcrypt.init_app(app)

    csrf.init_app(app)

    socketio.init_app(app)

    limiter.init_app(app)


def configure_jinja(app):

    @app.context_processor
    def inject_helpers():

        return {

            "display_name":
            extract_display_name,

            "format_dob":
            format_dob
        }

    app.jinja_env.globals.update(

        display_name=
        extract_display_name,

        format_dob=
        format_dob
    )


def configure_login_manager():

    login_manager.login_view = (
        "auth.login"
    )

    login_manager.login_message_category = (
        "warning"
    )

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(
            int(user_id)
        )





def register_blueprints(app):

    from app.auth import auth_bp

    from app.dashboard import (
        dashboard_bp
    )

    from app.admin import (
        admin_bp
    )

    from app.api.v1 import (
        api_v1
    )

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        dashboard_bp
    )

    app.register_blueprint(
        admin_bp
    )

    app.register_blueprint(
        api_v1
    )
