from flask_mail import Message

from app.extensions import mail


def send_otp_email(to_email, otp):

    try:

        print("EMAIL FUNCTION STARTED")

        msg = Message(

            subject="Your OTP Code",

            sender="sumantv.otp.service@gmail.com",

            recipients=[to_email],

            body=f"""

Your OTP Code is:

{otp}

Do not share this OTP with anyone.

            """.strip()

        )

        print("TRYING TO SEND EMAIL...")

        mail.send(msg)

        print("EMAIL SENT SUCCESS")

    except Exception as error:

        print(f"EMAIL ERROR: {error}")
