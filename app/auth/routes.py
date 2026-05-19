from flask import session

from datetime import datetime

from flask import (

    render_template,

    request,

    redirect,

    url_for,

    flash,

    session

)

from flask_login import (

    login_user,

    logout_user,

    login_required,

    current_user

)

from sqlalchemy import or_

from app.auth import auth_bp

from app.extensions import (

    db,

    bcrypt,

    limiter

)

from app.models.user import User

from app.utils.validators import (
    RequestValidator
)

from app.logging.audit import (
    log_action
)

from app.auth.decorators import (
    audit_action
)


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
@limiter.limit("20 per minute")
@audit_action("login_attempt")
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard.home"
            )
        )

    if request.method == "POST":

        email = (
            request.form.get("email", "")
            .strip()
            .lower()
        )

        password = (
            request.form.get("password", "")
            .strip()
        )

        if not email or not password:

            flash(
                "Email and password are required",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            log_action(

                user=email,

                action="failed_login",

                metadata={
                    "reason":
                    "user_not_found"
                }

            )

            flash(
                "Invalid email or password",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        valid_password = (
            bcrypt.check_password_hash(
                user.password_hash,
                password
            )
        )

        if not valid_password:

            log_action(

                user=email,

                action="failed_login",

                metadata={
                    "reason":
                    "invalid_password"
                }

            )

            flash(
                "Invalid email or password",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        if not user.is_active:

            flash(
                "Account disabled",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        login_user(

            user,

            remember=True

        )

        session.permanent = True

        log_action(

            user=user.email,

            action="successful_login",

            metadata={
                "ip":
                request.remote_addr
            }

        )


        return redirect(
            url_for(
                "dashboard.home"
            )
        )

    return render_template(

        "auth/login.html",

        page_title="Login"

    )


@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
@limiter.limit("5 per minute")
@audit_action("register_attempt")
def register():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    if request.method == "POST":

        first_name = (
            request.form.get("first_name", "")
            .strip()
        )

        last_name = (
            request.form.get("last_name", "")
            .strip()
        )

        display_name = (
            request.form.get("display_name", "")
            .strip()
        )

        username = display_name

        email = (
            request.form.get("email", "")
            .strip()
            .lower()
        )

        password = (
            request.form.get("password", "")
            .strip()
        )

        phone = request.form.get("phone", "").strip()

        date_of_birth_raw = request.form.get(
            "date_of_birth",
            ""
        ).strip()

        date_of_birth = None

        if date_of_birth_raw:

            try:

                formats = [

                    "%Y-%m-%d",

                    "%d/%m/%Y"
                ]

                for fmt in formats:

                    try:

                        date_of_birth = datetime.strptime(

                            date_of_birth_raw,

                            fmt

                        ).date()

                        break

                    except ValueError:

                        continue

            except ValueError:

                date_of_birth = None

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        marital_status = request.form.get(
            "marital_status",
            ""
        ).strip()

        nationality = request.form.get(
            "nationality",
            ""
        ).strip()

        blood_group = request.form.get(
            "blood_group",
            ""
        ).strip()

        employee_id = request.form.get(
            "employee_id",
            ""
        ).strip()

        bio = request.form.get(
            "bio",
            ""
        ).strip()

        try:

            RequestValidator.validate_registration({

                "username": username,

                "email": email,

                "password": password

            })

        except ValueError as error:

            flash(
                str(error),
                "warning"
            )

            return redirect(
                url_for("auth.register")
            )

        existing_user = User.query.filter(

            or_(

                User.email == email,

                User.username == username

            )

        ).first()

        if existing_user:

            flash(
                "User already exists",
                "warning"
            )

            return redirect(
                url_for("auth.register")
            )

        required_fields = {
            "First Name": first_name,
            "Last Name": last_name,
            "Display Name": display_name,
            "Email": email,
            "Password": password,
            "Employee ID": employee_id,
            "Gender": gender,
            "Marital Status": marital_status,
            "Date Of Birth": date_of_birth_raw,
        }

        for field_name, value in required_fields.items():

            if not value or not str(value).strip():

                flash(
                    f"{field_name} is required",
                    "warning"
                )

                return redirect(
                    url_for("auth.register")
                )


        password_hash = (
            bcrypt.generate_password_hash(
                password
            )
            .decode("utf-8")
        )

        from app.models.role import Role

        member_role = Role.query.filter_by(
            name="Member"
        ).first()
            

        user = User(

            username=username,

            email=email,

            password_hash=password_hash,

            first_name=first_name,

            last_name=last_name,
            
            role=member_role,

            display_name=display_name,

            phone=phone,

            date_of_birth=date_of_birth,

            gender=gender,

            marital_status=marital_status,

            nationality=nationality,

            blood_group=blood_group,

            employee_id=employee_id,

            bio=bio,

            is_active=True

        )

        db.session.add(user)

        db.session.commit()

        log_action(

            user=user.email,

            action="user_registered",

            metadata={
                "ip":
                request.remote_addr
            }

        )

        flash(
            "Registration successful",

            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(

        "auth/register.html",

        page_title="Register"

    )


@auth_bp.route("/logout")
@login_required
@limiter.limit("20 per minute")
@audit_action("logout")
def logout():

    user_email = current_user.email
       
    logout_user()

    log_action(

        user=user_email,

        action="successful_logout",

        metadata={
            "ip":
            request.remote_addr
        }

    )
    
    session.pop("_flashes", None)
    flash(
        "Logged out successfully",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )
