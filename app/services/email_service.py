import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

def send_otp_email(to_email, otp):

    try:

        response = resend.Emails.send({

            "from": "onboarding@resend.dev",

            "to": to_email,

            "subject": "Your OTP Code",

            "html": f"""

            <div style='font-family:Arial;'>

                <h2>Your OTP</h2>

                <h1>{otp}</h1>

            </div>

            """

        })

        print("EMAIL SENT SUCCESS")
        print(response)

    except Exception as error:

        print(f"EMAIL ERROR: {error}")
