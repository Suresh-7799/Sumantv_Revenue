from functools import wraps

from flask import (
    abort,
    request
)

from flask_login import (
    current_user
)

from app.logging.audit import (
    log_action
)


def verified_user_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:

            abort(401)

        if not getattr(

            current_user,

            "is_verified",

            False

        ):

            abort(403)

        return func(*args, **kwargs)

    return wrapper


def audit_action(action_name):

    def decorator(func):

        @wraps(func)

        def wrapper(*args, **kwargs):

            user = getattr(

                current_user,

                "email",

                "anonymous"

            )

            log_action(

                user=user,

                action=action_name,

                metadata={

                    "ip":
                    request.remote_addr

                }

            )

            return func(*args, **kwargs)

        return wrapper

    return decorator