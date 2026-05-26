from flask import session

from app.services.otp_service import OTPService

from app.services.email_service import (
    send_async_email
)

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
                "dashboard.overview"
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

        # =========================
        # EMAIL VERIFICATION
        # =========================

        if not user.is_email_verified:

            flash(
                "Please verify your email",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        # =========================
        # ADMIN APPROVAL CHECK
        # =========================

        if (

            user.role
            and user.role.name != "Admin"
            and user.approval_status.lower() != "approved"

        ):

            flash(
                "Waiting for admin approval",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        # =========================
        # ACCOUNT STATUS CHECK
        # =========================

        if (

            user.role
            and user.role.name != "Admin"
            and not user.is_active

        ):

            flash(
                "Account disabled",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # =========================
        # LOGIN USER
        # =========================

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
                "dashboard.overview"
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

    if request.method == "POST":

        first_name = (
            request.form.get(
                "first_name",
                ""
            ).strip()
        )

        email = (
            request.form.get(
                "email",
                ""
            ).strip()
            .lower()
        )

        password = (
            request.form.get(
                "password",
                ""
            ).strip()
        )

        employee_id = (
            request.form.get(
                "employee_id",
                ""
            ).strip()
        )

        if not all([
            first_name,
            email,
            password,
            employee_id
        ]):

            flash(
                "All fields are required",
                "warning"
            )

            return redirect(
                url_for("auth.register")
            )

        existing_user = User.query.filter(

            or_(

                User.email == email,

                User.employee_id == employee_id

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

        otp = OTPService.generate_otp()

        OTPService.store_otp(
            email,
            otp
        )

        session["pending_register"] = {

            "first_name": first_name,

            "email": email,

            "password": password,

            "employee_id": employee_id
        }

        send_async_email(

            subject="Your OTP Code",

            recipients=[email],

            body=f"Your OTP is: {otp}"
        )

        flash(
            "OTP sent to your email",
            "info"
        )

        return redirect(
            url_for(
                "auth.verify_otp"
            )
        )

    return render_template(

        "auth/register.html",

        page_title="Register"
    )

@auth_bp.route(
    "/verify-otp",
    methods=["GET", "POST"]
)
def verify_otp():

    pending = session.get(
        "pending_register"
    )

    if not pending:

        return redirect(
            url_for("auth.register")
        )

    if request.method == "POST":

        otp = request.form.get(
            "otp",
            ""
        ).strip()

        email = pending["email"]

        valid = OTPService.verify_otp(
            email,
            otp
        )

        if not valid:

            flash(
                "Invalid OTP",
                "danger"
            )

            return redirect(
                url_for("auth.verify_otp")
            )

        password_hash = (

            bcrypt.generate_password_hash(

                pending["password"]

            ).decode("utf-8")
        )

        from app.models.role import Role

        member_role = Role.query.filter_by(
            name="Member"
        ).first()

        user = User(

            username=
            pending["email"].split("@")[0],

            first_name=
            pending["first_name"],

            display_name=
            pending["first_name"],

            email=
            pending["email"],

            employee_id=
            pending["employee_id"],

            password_hash=
            password_hash,

            role=member_role,

            is_email_verified=True,

            is_active=False,

            approval_status="pending"
        )

        db.session.add(user)

        db.session.commit()

        session.pop(
            "pending_register",
            None
        )

        flash(

            "Registration successful. Wait for admin approval.",

            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/verify_otp.html"
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
