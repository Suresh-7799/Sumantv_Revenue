import os
import time
from datetime import datetime, date
from PIL import Image
from app.models.user import User
from app.models.chat_group import ChatGroup
from app.models.chat_group_member import ChatGroupMember

from app.services.chat_service import (
    save_chat_file
)

from app.models.chat_group import (
    ChatGroup
)

from app.models.chat_group_member import (
    ChatGroupMember
)

from app.models.chat_archive import (
    ChatArchive
)

from app.models.chat_block import (
    ChatBlock
)

from app.models.chat_message_visibility import (
    ChatMessageVisibility
)


from flask import (
    jsonify,
    current_app,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from app.services.chat_service import (
    save_chat_file
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

    users = User.query.filter(

        User.role_id == current_user.role_id,

        User.id != current_user.id

    ).all()

    return render_template(

        "dashboard/dashboard.html",

        users=users,

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


from flask import jsonify

from flask_login import login_required

from app.models.chat_message import (
    ChatMessage
)


@dashboard_bp.route(
    "/chat/messages/<int:user_id>"
)
@login_required
def get_chat_messages(user_id):

    messages = ChatMessage.query.filter(

        (
            (ChatMessage.sender_id == current_user.id)
            &
            (ChatMessage.receiver_id == user_id)
        )

        |

        (
            (ChatMessage.sender_id == user_id)
            &
            (ChatMessage.receiver_id == current_user.id)
        )

    ).order_by(
        ChatMessage.created_at.asc()
    ).all()

    result = []

    for msg in messages:

        created = msg.created_at

        if created.date() == datetime.utcnow().date():

            formatted = created.strftime(
                "%I:%M %p"
            )

        else:

            formatted = created.strftime(
                "%d %b %Y"
            )

        result.append({

            "id": msg.id,

            "sender_id": msg.sender_id,

            "receiver_id": msg.receiver_id,

            "message": msg.message,

            "file_url": msg.file_url,

            "file_name": msg.file_name,

            "file_type": msg.file_type,

            "deleted": msg.deleted,

            "created_at": formatted
        })

    return jsonify(result)


@dashboard_bp.route(
    "/chat/group/create",
    methods=["POST"]
)
@login_required
def create_group():

    data = request.json

    name = (
        data.get("name") or ""
    ).strip()

    members = data.get(
        "members",
        []
    )

    if not name:

        return jsonify({
            "success": False
        })

    group = ChatGroup(

        name=name,

        created_by=current_user.id
    )

    db.session.add(group)

    db.session.flush()

    creator = ChatGroupMember(

        group_id=group.id,

        user_id=current_user.id
    )

    db.session.add(creator)

    for user_id in members:

        existing = ChatGroupMember.query.filter_by(

            group_id=group.id,

            user_id=user_id

        ).first()

        if existing:

            continue

        member = ChatGroupMember(

            group_id=group.id,

            user_id=user_id
        )

        db.session.add(member)

    db.session.commit()

    return jsonify({

        "success": True,

        "group_id": group.id
    })


@dashboard_bp.route(
    "/chat/archive",
    methods=["POST"]
)
@login_required
def archive_chat():

    data = request.json

    conversation_id = data.get(
        "conversation_id"
    )

    existing = ChatArchive.query.filter_by(

        user_id=current_user.id,

        conversation_id=conversation_id

    ).first()

    if existing:

        return jsonify({
            "success": True
        })

    archive = ChatArchive(

        user_id=current_user.id,

        conversation_id=conversation_id
    )

    db.session.add(archive)

    db.session.commit()

    return jsonify({
        "success": True
    })


@dashboard_bp.route(
    "/chat/user/<int:user_id>"
)
@login_required
def chat_user_profile(user_id):

    user = User.query.get_or_404(
        user_id
    )

    return jsonify({

        "full_name":
        user.display_name,

        "first_name":
        user.first_name,

        "last_name":
        user.last_name,

        "email":
        user.email,

        "employee_id":
        user.employee_id,

        "role":
        user.role.name if user.role else "",

        "profile_image":
        user.profile_image,

        "banner":
        user.banner_image
    })

