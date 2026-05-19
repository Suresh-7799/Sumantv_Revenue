from functools import wraps

from flask import abort

from flask_login import current_user


def has_role(*roles):

    if (
        not current_user.is_authenticated or
        not current_user.role
    ):
        return False

    return (
        current_user.role.name in roles
    )


def role_required(*roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not has_role(*roles):
                abort(403)

            return func(*args, **kwargs)

        return wrapper

    return decorator
