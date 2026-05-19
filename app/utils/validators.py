from email_validator import (
    validate_email,
    EmailNotValidError
)


class RequestValidator:

    @staticmethod
    def validate_registration(data):

        required_fields = [

            "username",
            "email",
            "password"

        ]

        for field in required_fields:

            if not data.get(field):

                raise ValueError(
                    f"{field} is required"
                )

        try:

            validate_email(
                data["email"]
            )

        except EmailNotValidError:

            raise ValueError(
                "Invalid email address"
            )

        if len(data["password"]) < 8:

            raise ValueError(
                "Password too short"
            )

        return True