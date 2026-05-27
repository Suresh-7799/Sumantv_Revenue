import os

from dotenv import load_dotenv

from datetime import timedelta

load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    # =========================
    # DATABASE
    # =========================

    database_url = os.getenv(
        "DATABASE_URL"
    )

    if database_url:

        database_url = database_url.replace(

            "postgres://",

            "postgresql://"
        )

        if "sslmode=" not in database_url:

            database_url += "?sslmode=require"

    SQLALCHEMY_DATABASE_URI = (
        database_url
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # SECURITY
    # =========================

    MAX_CONTENT_LENGTH = (
        10 * 1024 * 1024
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY"
    )

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SECURE = (
        os.getenv(
            "SESSION_COOKIE_SECURE",
            "False"
        ) == "True"
    )

    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_HTTPONLY = True

    REMEMBER_COOKIE_SECURE = (
        os.getenv(
            "REMEMBER_COOKIE_SECURE",
            "False"
        ) == "True"
    )

    REMEMBER_COOKIE_SAMESITE = "Lax"

    PERMANENT_SESSION_LIFETIME = (
        timedelta(hours=2)
    )

    # =========================
    # MAIL
    # =========================

    MAIL_SERVER = os.getenv(
        "MAIL_SERVER"
    )

    MAIL_PORT = int(
        os.getenv(
            "MAIL_PORT",
            587
        )
    )

    MAIL_USE_TLS = (
        os.getenv(
            "MAIL_USE_TLS",
            "True"
        ) == "True"
    )

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME"
    )

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD"
    )

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER"
    )

    MAIL_SUPPRESS_SEND = False

    MAIL_TIMEOUT = 30


class DevelopmentConfig(Config):

    DEBUG = True


class ProductionConfig(Config):

    DEBUG = False

    SESSION_COOKIE_SECURE = True

    REMEMBER_COOKIE_SECURE = True
