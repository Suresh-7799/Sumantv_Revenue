import random

class OTPService:

    otp_store = {}

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
    def store_otp(email, otp):

        OTPService.otp_store[email] = otp

    @staticmethod
    def verify_otp(email, otp):

        stored_otp = OTPService.otp_store.get(email)

        if not stored_otp:

            return False

        return stored_otp == otp
