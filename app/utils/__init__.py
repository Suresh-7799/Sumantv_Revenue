from flask import Flask

from app.config.settings import (
    DevelopmentConfig
)

from app.extensions import (
    db,
    migrate,
    login_manager,
    bcrypt,
    csrf
)


def create_app():

    app = Flask(__name__)

    app.config.from_object(
        DevelopmentConfig
    )

    initialize_extensions(app)

    register_blueprints(app)

    return app


def initialize_extensions(app):

    db.init_app(app)

    migrate.init_app(app, db)

    login_manager.init_app(app)

    bcrypt.init_app(app)

    csrf.init_app(app)

    login_manager.login_view = (
        "auth.login"
    )


def register_blueprints(app):

    from app.auth import (
        auth_bp
    )

    from app.api.v1 import (
        api_v1
    )

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        api_v1
    )
