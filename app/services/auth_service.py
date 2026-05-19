from app.extensions import (
    bcrypt
)

from app.models.user import User

from app.services.base_service import (
    BaseService
)


class AuthService(BaseService):

    @staticmethod
    def register_user(data):

        existing_user = User.query.filter(
            (
                User.email ==
                data["email"]
            )
            |
            (
                User.username ==
                data["username"]
            )
        ).first()

        if existing_user:

            raise ValueError(
                "User already exists"
            )

        password_hash = (
            bcrypt.generate_password_hash(
                data["password"]
            )
            .decode("utf-8")
        )

        user = User(

            username=data["username"],

            email=data["email"],

            password_hash=password_hash

        )

        return AuthService.save(user)

    @staticmethod
    def authenticate_user(
        email,
        password
    ):

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            return None

        valid_password = (
            bcrypt.check_password_hash(
                user.password_hash,
                password
            )
        )

        if not valid_password:

            return None

        return user