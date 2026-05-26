from flask_mail import Message

from flask import current_app

from app.extensions import mail


def send_async_email(

    subject,

    recipients,

    body

):

    try:

        print("EMAIL FUNCTION STARTED")

        print(current_app.config["MAIL_USERNAME"])

        msg = Message(

            subject=subject,

            recipients=recipients,

            body=body,

            sender=current_app.config[
                "MAIL_USERNAME"
            ]

        )

        print("TRYING TO SEND EMAIL...")

        mail.send(msg)

        print("EMAIL SENT SUCCESS")

    except Exception as error:

        print(f"EMAIL ERROR: {error}")
