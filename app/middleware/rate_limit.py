from app.extensions import (
    limiter
)


def initialize_rate_limits(app):

    limiter.init_app(app)