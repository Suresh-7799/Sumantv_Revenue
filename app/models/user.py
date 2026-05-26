from datetime import datetime

from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        nullable=False,
        unique=True
    )

    email = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    first_name = db.Column(
        db.String(120),
        nullable=True
    )

    last_name = db.Column(
        db.String(120),
        nullable=True
    )

    display_name = db.Column(
        db.String(120),
        nullable=True
    )

    phone = db.Column(
        db.String(30),
        nullable=True
    )

    gender = db.Column(
        db.String(30),
        nullable=True
    )

    marital_status = db.Column(
        db.String(30),
        nullable=True
    )

    nationality = db.Column(
        db.String(120),
        nullable=True
    )

    blood_group = db.Column(
        db.String(20),
        nullable=True
    )

    employee_id = db.Column(
        db.String(50),
        nullable=True
    )

    bio = db.Column(
        db.Text,
        nullable=True
    )

    date_of_birth = db.Column(
        db.String(50),
        nullable=True
    )

    profile_image = db.Column(
        db.String(500),
        nullable=True
    )

    profile_image_updated_at = db.Column(
        db.DateTime,
        nullable=True
    )

    banner_image = db.Column(

        db.String(500),
   
        nullable=True
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id")
    )
    
    role = db.relationship(
        "Role",
        back_populates="users"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    is_email_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    approval_status = db.Column(
        db.String(30),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
