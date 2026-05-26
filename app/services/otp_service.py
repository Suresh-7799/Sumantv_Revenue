import random
import time


class OTPService:

    otp_store = {}

    OTP_EXPIRY_SECONDS = 300


    @staticmethod
    def generate_otp():

        return str(
            random.randint(
                100000,
                999999
            )
        )


    @classmethod
    def store_otp(

        cls,

        email,

        otp

    ):

        cls.otp_store[email] = {

            "otp": otp,

            "created_at": time.time()
        }


    @classmethod
    def verify_otp(

        cls,

        email,

        otp

    ):

        data = cls.otp_store.get(
            email
        )

        if not data:

            return False

        expired = (

            time.time()

            -

            data["created_at"]

            >

            cls.OTP_EXPIRY_SECONDS
        )

        if expired:

            cls.otp_store.pop(
                email,
                None
            )

            return False

        valid = (
            data["otp"] == otp
        )

        if valid:

            cls.otp_store.pop(
                email,
                None
            )

        return valid
