import os
import time
from datetime import datetime

from zoneinfo import ZoneInfo
from app.models.chat_message_visibility import ChatMessageVisibility


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

from werkzeug.utils import (
    secure_filename
)

from app.dashboard import (
    dashboard_bp
)

from app.extensions import (

    db,
    limiter,
    socketio
)

from app.models.user import (
    User
)

from app.models.chat_message import (
    ChatMessage
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

from app.services.chat_service import (
    save_chat_file
)


# =========================
# CONFIG
# =========================

ALLOWED_IMAGE_TYPES = {

    "image/jpeg",

    "image/png",

    "image/webp"
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024


# =========================
# INDEX
# =========================

@dashboard_bp.route("/")
def index():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard.home")
        )

    return redirect(
        url_for("auth.login")
    )


# =========================
# DASHBOARD
# =========================

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


# =========================
# PROFILE
# =========================

@dashboard_bp.route("/profile")
@login_required
def profile():

    return render_template(

        "profile/profile.html",

        active_page="profile"
    )


# =========================
# SETTINGS
# =========================

@dashboard_bp.route("/settings")
@login_required
def settings():

    return render_template(

        "profile/settings.html",

        active_page="settings"
    )


# =========================
# PROFILE IMAGE UPLOAD
# =========================

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

                "message":
                "No image uploaded"
            }), 400

        file = request.files["profile_image"]

        if not file:

            return jsonify({

                "success": False,

                "message":
                "Invalid image"
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
                "Image too large"
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

# =========================
# PROFILE UPDATE
# =========================

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


# =========================
# CHAT MESSAGES
# =========================

@dashboard_bp.route(
    "/chat/messages/<int:user_id>"
)
@login_required
def get_chat_messages(user_id):

    hidden_ids = [

        item.message_id

        for item in

        ChatMessageVisibility.query.filter_by(

            hidden_for_user_id=current_user.id

        ).all()
    ]



    messages = ChatMessage.query.filter(

        ChatMessage.deleted == False,

        ~ChatMessage.id.in_(hidden_ids),

        (

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
        )

    ).order_by(

        ChatMessage.created_at.asc()

    ).all()

    results = []

    for msg in messages:

        results.append({

            "id":
            msg.id,

            "sender_id":
            msg.sender_id,

            "receiver_id":
            msg.receiver_id,

            "message":
            msg.message,

            "file_url":
            msg.file_url,

            "file_name":
            msg.file_name,

            "file_size":
            msg.file_size,

            "file_type":
            msg.file_type,

            "file_category":
            msg.file_category,

            "created_at":
            msg.created_at.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).strftime("%I:%M %p")
            if msg.created_at.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).date() == datetime.now(
                ZoneInfo("Asia/Kolkata")
            ).date()
            else
            msg.created_at.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).strftime("%d %b %Y"),

            "deleted":
            msg.deleted,

            "is_read":
            msg.is_read
        })

    return jsonify(results)


# =========================
# CHAT FILE UPLOAD
# =========================

@dashboard_bp.route(
    "/chat/upload",
    methods=["POST"]
)
@login_required
@limiter.limit("30/minute")
def upload_chat_file():

    try:

        if "file" not in request.files:

            return jsonify({

                "success": False,

                "message":
                "No file uploaded"
            }), 400

        file = request.files["file"]

        data = save_chat_file(file)

        return jsonify({

            "success": True,

            "file": data
        })

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message":
            str(error)
        }), 400


# =========================
# CREATE GROUP
# =========================

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
    members = list(set(members))
    if not name:

        return jsonify({

            "success": False
        }), 400

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

        try:

            user_id = int(user_id)

        except (TypeError, ValueError):

            continue

        if user_id == current_user.id:
            continue

        member = ChatGroupMember(

            group_id=group.id,

            user_id=user_id
        )

        db.session.add(member)

    db.session.commit()

    return jsonify({

        "success": True,

        "group_id":
        group.id
    })


# =========================
# ARCHIVE CHAT
# =========================

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
    if not conversation_id:

        return jsonify({

            "success": False
        }), 400

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


# =========================
# BLOCK USER
# =========================




# =========================
# USER PROFILE API
# =========================

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
        user.display_name or "",

        "first_name":
        user.first_name or "",

        "last_name":
        user.last_name or "",

        "email":
        user.email or "",

        "employee_id":
        user.employee_id or "",
    
        "role":
        user.role.name if user.role else "",

        "profile_image":
        user.profile_image or "",

        "banner":
        user.banner_image or ""
    })


# =========================
# BANNER UPLOAD
# =========================

@dashboard_bp.route("/upload-banner-image", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def upload_banner_image():

    try:

        if "banner" not in request.files:
            return jsonify({
                "success": False,
                "message": "No image uploaded"
            }), 400

        image = request.files["banner"]

        if not image or image.filename == "":
            return jsonify({
                "success": False,
                "message": "Invalid image"
            }), 400

        allowed_extensions = {"png", "jpg", "jpeg", "webp"}

        extension = image.filename.rsplit(".", 1)[-1].lower()

        image.seek(0, os.SEEK_END)

        file_size = image.tell()

        image.seek(0)

        if file_size > MAX_IMAGE_SIZE:

            return jsonify({

                "success": False,

                "message": "Image too large"

            }), 400

        if extension not in allowed_extensions:
            return jsonify({
                "success": False,
                "message": "Unsupported image format"
            }), 400

        upload_dir = os.path.join(
            current_app.static_folder,
            "uploads",
            "banners"
        )

        os.makedirs(upload_dir, exist_ok=True)

        filename = (
            f"banner_{current_user.id}_{int(time.time())}.webp"
        )

        save_path = os.path.join(upload_dir, filename)

        try:

            img = Image.open(image).convert("RGB")

        except Exception:

            return jsonify({

                "success": False,

                "message": "Invalid image"

            }), 400

        img.save(
            save_path,
            "WEBP",
            quality=85
        )

        banner_url = url_for(
            "static",
            filename=f"uploads/banners/{filename}"
        )

        old_banner = current_user.banner_image

        current_user.banner_image = banner_url

        db.session.commit()

        if old_banner:

            try:

                old_path = os.path.join(
                    current_app.root_path,
                    old_banner.lstrip("/")
                )

                if os.path.exists(old_path):
                    os.remove(old_path)

            except Exception:
                pass

        return jsonify({
            "success": True,
            "banner_url": banner_url
        })

    except Exception as error:

        current_app.logger.exception(error)

        return jsonify({
            "success": False,
            "message": "Banner upload failed"
        }), 500

# =========================
# CLEAR CHAT
# =========================

@dashboard_bp.route(
    "/chat/clear",
    methods=["POST"]
)
@login_required
def clear_chat():

    data = request.json

    receiver_id = data.get(
        "receiver_id"
    )

    if not receiver_id:

        return jsonify({

            "success": False,

            "message":
            "Receiver missing"
        }), 400

    messages = ChatMessage.query.filter(

        ChatMessage.deleted == False,

        (

            (
                ChatMessage.sender_id
                ==
                current_user.id
            )

            &

            (
                ChatMessage.receiver_id
                ==
                receiver_id
            )

        )

        |

        (

            (
                ChatMessage.sender_id
                ==
                receiver_id
            )

            &

            (
                ChatMessage.receiver_id
                ==
                current_user.id
            )

        )

    ).all()

    for msg in messages:

        existing = ChatMessageVisibility.query.filter_by(

            message_id=msg.id,

            hidden_for_user_id=current_user.id

        ).first()

        if existing:

            continue

        hidden = ChatMessageVisibility(

            message_id=msg.id,

            hidden_for_user_id=current_user.id
        )

        db.session.add(hidden)

    db.session.commit()

    return jsonify({

        "success": True
    })


# =========================
# UNARCHIVE CHAT
# =========================

@dashboard_bp.route(
    "/chat/unarchive",
    methods=["POST"]
)
@login_required
def unarchive_chat():

    data = request.json

    conversation_id = data.get(
        "conversation_id"
    )

    archive = ChatArchive.query.filter_by(

        user_id=current_user.id,

        conversation_id=conversation_id

    ).first()

    if archive:

        db.session.delete(
            archive
        )

        db.session.commit()

    return jsonify({

        "success": True
    })


# =========================
# UNBLOCK USER
# =========================

@dashboard_bp.route(
    "/chat/unblock-user",
    methods=["POST"]
)
@login_required
def unblock_user():

    data = request.json

    blocked_id = data.get(
        "user_id"
    )

    if not blocked_id:

        return jsonify({

            "success": False
        }), 400

    block = ChatBlock.query.filter_by(

        blocker_id=current_user.id,

        blocked_id=blocked_id

    ).first()

    if block:

        db.session.delete(
            block
        )

        db.session.commit()

    return jsonify({

        "success": True
    })


# =========================
# ONLINE USERS
# =========================

@dashboard_bp.route(
    "/chat/online-users"
)
@login_required
def get_online_users():

    from app.realtime.socket import (
        online_users
    )

    return jsonify({

        "users":
        [list(map(int, online_users))]
    })


# =========================
# HEALTH CHECK
# =========================

@dashboard_bp.route(
    "/chat/health"
)
@login_required
def chat_health():

    return jsonify({

        "success": True,

        "socket": True,

        "chat": True
    })

# =========================
# DELETE MESSAGE
# =========================

@dashboard_bp.route(
    "/chat/delete-message",
    methods=["POST"]
)
@login_required
def delete_message():

    data = request.get_json()

    message_id = data.get(
        "message_id"
    )

    if not message_id:

        return jsonify({
            "success": False,
            "message": "Message ID missing"
        }), 400

    message = ChatMessage.query.filter_by(
        id=message_id,
        sender_id=current_user.id
    ).first()

    if not message:

        return jsonify({
            "success": False,
            "message": "Message not found"
        }), 404

    message.deleted = True

    db.session.commit()

    socketio.emit(
        "message_deleted",
        {
            "message_id": message.id
        }
    )

    return jsonify({
        "success": True
    })


# =========================
# CHAT SEARCH
# =========================

@dashboard_bp.route(
    "/chat/search"
)
@login_required
@limiter.limit("30/minute")
def search_chat_users():

    query = (
        request.args.get("q") or ""
    ).strip()

    if len(query) < 2:

        return jsonify([])

    users = User.query.filter(

        User.id != current_user.id,

        User.display_name.isnot(None),

        User.display_name.ilike(
            f"%{query}%"
        )

    ).limit(20).all()

    results = []

    for user in users:

        results.append({

            "id":
            user.id,

            "name":
            user.display_name,

            "avatar":
            user.profile_image or "/static/default-avatar.png",

            "role":
            user.role.name if user.role else ""
        })

    return jsonify(results)


# =========================
# GET GROUPS
# =========================

@dashboard_bp.route(
    "/chat/groups"
)
@login_required
def get_groups():

    memberships = ChatGroupMember.query.filter_by(

        user_id=current_user.id

    ).all()

    groups = []

    for membership in memberships:

        group = ChatGroup.query.get(
            membership.group_id
        )

        if not group:

            continue

        groups.append({

            "id":
            group.id,

            "name":
            group.name
        })

    return jsonify(groups)


# =========================
# GET GROUP MESSAGES
# =========================

@dashboard_bp.route(
    "/chat/group/<int:group_id>/messages"
)
@login_required
def get_group_messages(group_id):

    membership = ChatGroupMember.query.filter_by(

        group_id=group_id,

        user_id=current_user.id

    ).first()

    if not membership:

        return jsonify({

            "success": False,

            "message":
            "Access denied"
        }), 403

    messages = ChatMessage.query.filter(

        ChatMessage.group_id == group_id,

        ChatMessage.deleted == False

    ).order_by(

        ChatMessage.created_at.asc()

    ).all()

    results = []

    for msg in messages:

        results.append({

            "id":
            msg.id,

            "group_id":
            msg.group_id,

            "sender_id":
            msg.sender_id,

            "sender_name":
            msg.sender.display_name
            if msg.sender else "User",

            "message":
            msg.message,

            "file_url":
            msg.file_url,

            "file_name":
            msg.file_name,

            "file_type":
            msg.file_type,

            "created_at":
            msg.created_at.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).strftime("%I:%M %p")
            if msg.created_at.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).date() == datetime.now(
                ZoneInfo("Asia/Kolkata")
            ).date()
            else
            msg.created_at.astimezone(
                ZoneInfo("Asia/Kolkata")
            ).strftime("%d %b %Y"),

        })

    return jsonify(results)


# =========================
# ARCHIVED CHATS
# =========================

@dashboard_bp.route(
    "/chat/archived"
)
@login_required
def archived_chats():

    archives = ChatArchive.query.filter_by(

        user_id=current_user.id

    ).all()

    results = []

    for archive in archives:

        results.append({

            "conversation_id":
            archive.conversation_id
        })

    return jsonify(results)


# =========================
# BLOCKED USERS
# =========================

@dashboard_bp.route(
    "/chat/blocked-users"
)
@login_required
def blocked_users():

    blocks = ChatBlock.query.filter_by(

        blocker_id=current_user.id

    ).all()

    results = []

    for block in blocks:

        user = User.query.get(
            block.blocked_id
        )

        if not user:

            continue

        results.append({

            "id":
            user.id,

            "name":
            user.display_name,

            "avatar":
            user.profile_image
        })

    return jsonify(results)




# =========================
# DELETE FOR ME
# =========================

@dashboard_bp.route(

    "/chat/delete-for-me",

    methods=["POST"]
)

@login_required
def delete_message_for_me():

    data = request.get_json()

    message_id = data.get(
        "message_id"
    )

    if not message_id:

        return jsonify({

            "success": False

        }), 400

    message = ChatMessage.query.get(
        message_id
    )

    if not message:

        return jsonify({

            "success": False

        }), 404

    existing = ChatMessageVisibility.query.filter_by(

        message_id=message.id,

        hidden_for_user_id=current_user.id

    ).first()

    if existing:

        return jsonify({

            "success": True
        })

    visibility = ChatMessageVisibility(

        message_id=message.id,

        hidden_for_user_id=current_user.id
    )

    db.session.add(
        visibility
    )

    db.session.commit()

    return jsonify({

        "success": True
    })


# =========================
# FORWARD MESSAGE
# =========================

@dashboard_bp.route(

    "/chat/forward-message",

    methods=["POST"]
)

@login_required
def forward_message():

    data = request.get_json()

    receiver_id = data.get(
        "receiver_id"
    )

    message = data.get(
        "message"
    )

    if not receiver_id or not message:

        return jsonify({

            "success":False

        }),400

    new_message = ChatMessage(

        sender_id=current_user.id,

        receiver_id=receiver_id,

        message=message
    )

    db.session.add(
        new_message
    )

    db.session.commit()

    socketio.emit(

        "new_message",

        {

            "id":new_message.id,

            "sender_id":
            current_user.id,

            "receiver_id":
            receiver_id,

            "message":
            message,

            "created_at":
            new_message.created_at.strftime(
                "%I:%M %p"
            )
        },

        room=f"user_{receiver_id}"
    )

    return jsonify({

        "success":True
    })

