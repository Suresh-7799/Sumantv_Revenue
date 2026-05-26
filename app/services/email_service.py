import smtplib
import socket

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import current_app


def send_otp_email(to_email, otp):

    try:

        smtp_server = current_app.config["MAIL_SERVER"]
        smtp_port = current_app.config["MAIL_PORT"]

        sender_email = current_app.config["MAIL_USERNAME"]
        sender_password = current_app.config["MAIL_PASSWORD"]

        message = MIMEMultipart()

        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = "Your OTP Code"

        body = f"""

Your OTP Code is:

{otp}

Do not share this OTP with anyone.

        """

        message.attach(
            MIMEText(body, "plain")
        )

        socket.setdefaulttimeout(30)

        server = smtplib.SMTP(
            smtp_server,
            smtp_port
        )

        server.ehlo()

        server.starttls()

        server.login(
            sender_email,
            sender_password
        )

        server.sendmail(
            sender_email,
            to_email,
            message.as_string()
        )

        server.quit()

        print("EMAIL SENT SUCCESS")

    except Exception as error:

        print(f"EMAIL ERROR: {error}")
