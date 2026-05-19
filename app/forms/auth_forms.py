from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    SelectField
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length
)


class LoginForm(FlaskForm):

    email = StringField(
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )


class RegisterForm(FlaskForm):

    first_name = StringField(
        validators=[
            DataRequired(),
            Length(min=2,max=50)
        ]
    )

    last_name = StringField(
        validators=[
            DataRequired(),
            Length(min=2,max=50)
        ]
    )

    display_name = StringField(
        validators=[
            DataRequired(),
            Length(min=2,max=50)
        ]
    )

    email = StringField(
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        validators=[
            DataRequired(),
            Length(min=6,max=128)
        ]
    )

    phone = StringField()

    employee_id = StringField()

    gender = SelectField(
        choices=[
            ("Male","Male"),
            ("Female","Female")
        ]
    )

    marital_status = SelectField(
        choices=[
            ("","Select"),
            ("Single","Single"),
            ("Married","Married")
        ]
    )

    nationality = StringField()

    blood_group = StringField()

    bio = TextAreaField()
