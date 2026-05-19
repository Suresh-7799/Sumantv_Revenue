from itsdangerous import (

    URLSafeTimedSerializer,

    SignatureExpired,

    BadSignature

)

from flask import current_app


def generate_token(email):

    serializer = URLSafeTimedSerializer(

        current_app.config["SECRET_KEY"]

    )

    return serializer.dumps(

        email,

        salt="auth-token"

    )


def verify_token(

    token,

    expiration=3600

):

    serializer = URLSafeTimedSerializer(

        current_app.config["SECRET_KEY"]

    )

    try:

        email = serializer.loads(

            token,

            salt="auth-token",

            max_age=expiration

        )

        return email

    except SignatureExpired:

        return None

    except BadSignature:

        return None