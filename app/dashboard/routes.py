import os
import time
from datetime import datetime, date
from PIL import Image

from flask import (
    jsonify,
    current_app,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from app.dashboard import dashboard_bp

from app.extensions import (
    db,
    limiter
)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024


@dashboard_bp.route("/")
def index():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard.home")
        )

    return redirect(
        url_for("auth.login")
    )


@dashboard_bp.route("/dashboard")
@login_required
def home():

    return render_template(
        "dashboard/dashboard.html",
        active_page="overview"
    )


@dashboard_bp.route("/profile")
@login_required
def profile():

    return render_template(
        "profile/profile.html",
        active_page="profile"
    )


@dashboard_bp.route("/settings")
@login_required
def settings():

    return render_template(
        "profile/settings.html",
        active_page="settings"
    )


@dashboard_bp.route(
    "/profile/upload-image",
    methods=["POST"]
)
@limiter.limit("10/minute")
@login_required
def upload_profile_image():

    try:

        if "profile_image" not in request.files:

            return jsonify({

                "success": False,

                "message": "No image uploaded"
            }), 400

        file = request.files["profile_image"]

        if not file:

            return jsonify({

                "success": False,

                "message": "Invalid image"
            }), 400

        if file.mimetype not in ALLOWED_IMAGE_TYPES:

            return jsonify({

                "success": False,

                "message": "Unsupported image type"
            }), 400

        file.seek(0, os.SEEK_END)

        file_size = file.tell()

        file.seek(0)

        if file_size > MAX_IMAGE_SIZE:

            return jsonify({

                "success": False,

                "message": "Image too large"
            }), 400

        timestamp = int(time.time())

        user_folder = os.path.join(

            current_app.static_folder,

            "uploads",

            "profile",

            str(current_user.id)
        )

        os.makedirs(

            user_folder,

            exist_ok=True
        )

        filename = secure_filename(

            f"avatar_v{timestamp}.webp"
        )

        absolute_file_path = os.path.join(

            user_folder,

            filename
        )

        image = Image.open(file)

        image = image.convert("RGB")

        image.thumbnail(
            (600, 600)
        )

        image.save(

            absolute_file_path,

            "WEBP",

            quality=90,

            method=6
        )

        old_image = current_user.profile_image

        current_user.profile_image = (

            f"/static/uploads/profile/"
            f"{current_user.id}/"
            f"{filename}"
        )

        current_user.profile_image_updated_at = (
            datetime.utcnow()
        )

        db.session.commit()

        if old_image:

            try:

                old_absolute_path = os.path.join(

                    current_app.root_path,

                    old_image.lstrip("/")
                )

                if os.path.exists(
                    old_absolute_path
                ):

                    os.remove(
                        old_absolute_path
                    )

            except Exception:

                pass

        return jsonify({

            "success": True,

            "image_url":
            current_user.profile_image,

            "message":
            "Profile image updated"
        })

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message":
            str(error)
        }), 500


@dashboard_bp.route(

    "/upload-banner",

    methods=["POST"]
)
@limiter.limit("10/minute")
@login_required
def upload_banner():

    try:

        if "banner" not in request.files:

            return jsonify({

                "success": False,

                "message":
                "No banner uploaded"
            }), 400

        file = request.files["banner"]

        if not file:

            return jsonify({

                "success": False,

                "message":
                "Invalid banner image"
            }), 400

        if file.mimetype not in ALLOWED_IMAGE_TYPES:

            return jsonify({

                "success": False,

                "message":
                "Unsupported image type"
            }), 400

        file.seek(0, os.SEEK_END)

        file_size = file.tell()

        file.seek(0)

        if file_size > MAX_IMAGE_SIZE:

            return jsonify({

                "success": False,

                "message":
                "Banner image too large"
            }), 400

        timestamp = int(time.time())

        user_folder = os.path.join(

            current_app.static_folder,

            "uploads",

            "banners",

            str(current_user.id)
        )

        os.makedirs(

            user_folder,

            exist_ok=True
        )

        filename = secure_filename(

            f"banner_v{timestamp}.webp"
        )

        absolute_file_path = os.path.join(

            user_folder,

            filename
        )

        image = Image.open(file)

        image = image.convert("RGB")

        image.thumbnail(
            (1800, 700)
        )

        image.save(

            absolute_file_path,

            "WEBP",

            quality=92,

            method=6
        )

        old_banner = current_user.banner_image

        current_user.banner_image = (

            f"/static/uploads/banners/"
            f"{current_user.id}/"
            f"{filename}"
        )

        db.session.commit()

        # REMOVE OLD BANNER

        if old_banner:

            try:

                old_absolute_path = os.path.join(

                    current_app.root_path,

                    old_banner.lstrip("/")
                )

                if os.path.exists(
                    old_absolute_path
                ):

                    os.remove(
                        old_absolute_path
                    )

            except Exception:

                pass

        return jsonify({

            "success": True,

            "banner_url":
            current_user.banner_image,

            "message":
            "Banner updated successfully"
        })

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message":
            str(error)
        }), 500


@dashboard_bp.route(
    "/profile/update",
    methods=["POST"]
)
@login_required
def update_profile():

    allowed_fields = [

        "first_name",

        "last_name",

        "display_name",

        "gender",

        "date_of_birth",

        "blood_group",

        "nationality",

        "bio",

        "marital_status"
    ]

    for field in allowed_fields:

        value = request.form.get(
           field,
            ""
        ).strip()

    if field == "date_of_birth":

        if value:

            try:

                parsed = None

                formats = [
                
                    "%Y-%m-%d",

                    "%d/%m/%Y"
                ]

                for fmt in formats:

                    try:

                        parsed = datetime.strptime(
                            value,
                            fmt
                        ).date()

                        break

                    except ValueError:

                        continue

                value = parsed

            except ValueError:

                value = None

        else:

            value = None

    setattr(

        current_user,

        field,

        value
    )

    db.session.commit()

    flash(
        "Profile updated successfully",
        "success"
    )

    return redirect(
        url_for("dashboard.profile")
    )
