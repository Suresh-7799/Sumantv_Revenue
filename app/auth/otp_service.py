import random

from datetime import (
    datetime,
    timedelta
)

from app.extensions import (
    redis_client
)


class OTPService:

    OTP_EXPIRATION = 300

    @staticmethod
    def generate_otp():

        return str(

            random.randint(
                100000,
                999999
            )

        )

    @staticmethod
    def store_otp(

        email,

        otp

    ):

        redis_client.setex(

            f"otp:{email}",

            OTPService.OTP_EXPIRATION,

            otp

        )

    @staticmethod
    def verify_otp(

        email,

        otp

    ):

        stored_otp = redis_client.get(

            f"otp:{email}"

        )

        if not stored_otp:

            return False

        return stored_otp == otp