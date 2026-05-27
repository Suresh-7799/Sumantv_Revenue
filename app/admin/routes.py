from flask import (

    render_template,

    request,

    redirect,

    url_for,

    flash,

    abort

)

from flask_login import (

    login_required,

    current_user

)

from sqlalchemy import or_

from datetime import datetime

from app.admin import admin_bp

from app.extensions import db

from app.models.user import User
from app.models.role import Role

from app.utils.rbac import (

    role_required,

    has_role

)


@admin_bp.route("/team")
@login_required
@role_required("Admin")
def team():

    search = request.args.get(
        "search",
        ""
    ).strip()

    users_query = User.query

    if search:

        users_query = users_query.filter(

            or_(

                User.first_name.ilike(f"%{search}%"),

                User.last_name.ilike(f"%{search}%"),

                User.display_name.ilike(f"%{search}%"),

                User.email.ilike(f"%{search}%"),

                User.phone.ilike(f"%{search}%"),

                User.employee_id.ilike(f"%{search}%")

            )

        )

    approved_users = User.query.filter(

        User.id != current_user.id,

        User.approval_status == "approved"

    ).all()

    pending_users = User.query.filter(

        User.id != current_user.id,

        User.approval_status == "pending"

    ).all()

    return render_template(

        "admin/team.html",

        users=approved_users,

        pending_users=pending_users,

        search=search,

        active_page="team"

    )


@admin_bp.route("/user/<int:user_id>")
@login_required
@role_required("Admin")
def user_details(user_id):

    user = User.query.get_or_404(user_id)

    roles = Role.query.all()

    return render_template(

        "admin/user_details.html",

        user=user,

        roles=roles,

        active_page="team"

    )


@admin_bp.route(
    "/user/<int:user_id>/update",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def update_user(user_id):

    user = User.query.get_or_404(user_id)

    user.first_name = request.form.get(
        "first_name",
        ""
    ).strip()

    user.last_name = request.form.get(
        "last_name",
        ""
    ).strip()

    user.display_name = request.form.get(
        "display_name",
        ""
    ).strip()

    user.email = request.form.get(
        "email",
        ""
    ).strip()

    user.phone = request.form.get(
        "phone",
        ""
    ).strip()

    user.employee_id = request.form.get(
        "employee_id",
        ""
    ).strip()

    user.gender = request.form.get(
        "gender",
        ""
    ).strip()

    date_of_birth = request.form.get(
        "date_of_birth",
        ""
    ).strip()

    if date_of_birth:

        try:

            parsed = None

            formats = [

                "%Y-%m-%d",

                "%d/%m/%Y"
            ]

            for fmt in formats:

                try:

                    parsed = datetime.strptime(

                        date_of_birth,

                        fmt

                    ).date()

                    break

                except ValueError:

                    continue

            user.date_of_birth = parsed

        except ValueError:

            user.date_of_birth = None

    else:

        user.date_of_birth = None

    user.blood_group = request.form.get(
        "blood_group",
        ""
    ).strip()

    user.nationality = request.form.get(
        "nationality",
        ""
    ).strip()

    user.bio = request.form.get(
        "bio",
        ""
    ).strip()

    # =========================
    # ROLE HANDLING
    # =========================

    custom_role = request.form.get(
        "custom_role",
        ""
    ).strip()

    selected_role_id = request.form.get(
        "role_id"
    )

    is_self_update = user.id == current_user.id

    role = None

    # custom role create

    if custom_role:

        existing_role = Role.query.filter_by(
            name=custom_role
        ).first()

        if existing_role:

            role = existing_role

        else:

            role = Role(
                name=custom_role
            )

            db.session.add(role)

            db.session.flush()

    # dropdown role

    elif selected_role_id:

        role = Role.query.get(
            selected_role_id
        )

    # prevent assigning Admin

    if role and role.name == "Admin":

        flash(
            "Admin role cannot be assigned from panel",
            "warning"
        )

        return redirect(
            url_for(
                "admin.user_details",
                user_id=user.id
            )
        )

    if role:

        if is_self_update:

            flash(
                "You cannot change your own admin role",
                "warning"
            )

        else:

            user.role = role

    user.is_active = (
        True
        if request.form.get("is_active")
        else False
    )

    db.session.commit()

    flash(
        "Employee updated successfully",
        "success"
    )

    return redirect(
        url_for(
            "admin.user_details",
            user_id=user.id
        )
    )


@admin_bp.route(
    "/approve-user/<int:user_id>",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def approve_user(user_id):

    user = User.query.get_or_404(
        user_id
    )

    user.approval_status = (
        "approved"
    )

    user.is_active = True

    db.session.commit()

    return {

        "success": True
    }

@admin_bp.route(
    "/reject-user/<int:user_id>",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def reject_user(user_id):

    user = User.query.get_or_404(
        user_id
    )

    db.session.delete(user)

    db.session.commit()

    return {

        "success": True
    }
