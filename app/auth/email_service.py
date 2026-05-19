from flask_mail import (
    Message
)

from flask import (
    current_app
)

from app.extensions import (
    mail
)

from app.queues.celery_app import (
    celery
)


@celery.task
def send_async_email(

    subject,

    recipients,

    body

):

    msg = Message(

        subject=subject,

        recipients=recipients,

        body=body

    )

    with current_app.app_context():

        mail.send(msg)


class EmailService:

    @staticmethod
    def send_password_reset(

        user,

        reset_link

    ):

        send_async_email.delay(

            subject="Password Reset",

            recipients=[user.email],

            body=(
                f"Reset your password:\\n"
                f"{reset_link}"
            )

        )

    @staticmethod
    def send_verification_email(

        user,

        verification_link

    ):

        send_async_email.delay(

            subject="Verify Email",

            recipients=[user.email],

            body=(
                f"Verify your account:\\n"
                f"{verification_link}"
            )

        )