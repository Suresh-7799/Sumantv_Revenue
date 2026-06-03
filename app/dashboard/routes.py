import os
import time
from datetime import datetime

from app.models.commercial_channel import CommercialChannel
from app.models.commercial_client import CommercialClient
from app.models.commercial_result import CommercialResult

import csv
from io import StringIO
from flask import Response

from app.models.youtube_tracking import (
    YoutubeTracking
)

from yt_dlp import YoutubeDL
import traceback

import threading

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

SCAN_RUNNING = False

COMMERCIAL_SCAN_RUNNING = False


from app.models.youtube_channel import YoutubeChannel


from app.models.youtube_strip_result import (
    YoutubeStripResult
)

from app.extensions import db


from app.services.youtube_ocr_service import (
    scan_youtube_video
)

from app.services.youtube_tracking_ocr import (
    scan_youtube_video as tracking_scan_youtube_video
)

from app.services.commercials.channel_scraper import (
    get_latest_videos
)

from app.services.commercials.commercial_scanner import (
    process_frames
)

from app.services.commercials.video_downloader import (
    download_video
)

from app.services.commercials.frame_extractor import (
    extract_frames
)

from app.dashboard import dashboard_bp

from app.realtime.socket import (
    format_timestamp
)

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

import json

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


def background_scan(

    app,

    channel_id,

    video_count
):
    
    print(
        "\nBACKGROUND SCAN STARTED\n"
    )
    

    global SCAN_RUNNING

    with app.app_context():

        SCAN_RUNNING = True

        try:

            channel = YoutubeChannel.query.get(
                channel_id
            )

            if not channel:

                return

            ydl_opts = {

                "extract_flat": True,

                "quiet": True,

                "ignoreerrors": True
                
            }
            

            with YoutubeDL(
                ydl_opts
            ) as ydl:

                playlist_url = channel.channel_url

                if not playlist_url.endswith("/videos"):

                    playlist_url += "/videos"

                info = ydl.extract_info(

                    playlist_url,

                    download=False
                )

                entries = info.get(
                    "entries",
                    []
                )

                entries = list(entries)[
                    :video_count
                ]

                print(
                    f"TOTAL ENTRIES : {len(entries)}"
                )


            def process_video(entry):

                with app.app_context():

                    global SCAN_RUNNING

                    if not SCAN_RUNNING:

                        return

                    video_id = entry.get(
                        "id"
                    )

                    if not video_id:

                        return

                    video_url = (

                        f"https://www.youtube.com/watch?v="
                        f"{video_id}"
                    )

                    print(
                        f"VIDEO = {video_url}"
                    )

                    existing_result = (
                        YoutubeStripResult.query.filter_by(
                            video_url=video_url
                        ).first()
                    )

                    if existing_result:

                        return

                    try:

                        print(
                            f"OCR START : {video_url}"
                        )

                        scan_data = scan_youtube_video(
                            video_url
                        )

                    except Exception as error:

                        print(error)

                        return

                    results = scan_data.get(
                        "results",
                        []
                    )

                    if (

                        not results

                        or

                        results[0]["text"] == "No Strip Found"
                    ):

                        return

                    matched_strip = " | ".join(

                        [
                            item["text"]
                            for item in results[:5]
                        ]
                    )

                    data = YoutubeStripResult(

                        channel_name=channel.channel_name,

                        video_title=scan_data.get(
                            "video_title"
                        ),

                        video_url=video_url,

                        strip_text=matched_strip,

                        detected_time=results[0]["time"]
                    )

                    db.session.add(data)

                    db.session.commit()

                    print(
                        f"Saved: {video_url}"
                    )

            print(
                "THREAD START"
            )

            with ThreadPoolExecutor(
                max_workers=3
            ) as executor:

                futures = [

                    executor.submit(
                        process_video,
                        entry
                    )

                    for entry in entries
                ]

                for future in as_completed(
                    futures
                ):

                    try:

                        future.result()

                    except Exception as error:

                        print(
                            f"THREAD ERROR : {error}"
                        )

        except Exception as error:

            print(
                "\nSCAN ERROR\n"
            )

            print(
                error
            )

            traceback.print_exc()

            print(
                f"ERROR = {error}"
            )

        finally:

            db.session.remove()

            SCAN_RUNNING = False

            print(
                "\nSCAN STOPPED\n"
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
            url_for(
                "dashboard.overview"
            )
        )

    return redirect(
        url_for(
            "auth.login"
        )
    )

# =========================
# DASHBOARD
# =========================

@dashboard_bp.route("/dashboard")
@login_required
def dashboard_redirect():

    return redirect(
        url_for(
            "dashboard.overview"
        )
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

    # =========================
    # ADMIN ONLY FIELDS
    # =========================

    if (

        current_user.role

        and

        current_user.role.name == "Admin"
    ):

        email = request.form.get(
            "email"
        )

        employee_id = request.form.get(
            "employee_id"
        )

        phone = request.form.get(
            "phone"
        )

        if email and email.strip():

            current_user.email = (
                email.strip()
            )

        if employee_id and employee_id.strip():

            current_user.employee_id = (
                employee_id.strip()
            )

        if phone and phone.strip():

            current_user.phone = (
                phone.strip()
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
            format_timestamp(
                msg.created_at
            ),

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



@dashboard_bp.route("/overview")
@login_required
def overview():

    users = User.query.filter(

        User.role_id == current_user.role_id,

        User.id != current_user.id

    ).all()

    return render_template(

        "dashboard/overview.html",

        active_page="overview",

        users=users
    )


@dashboard_bp.route("/revenue")
@login_required
def revenue():

    users = User.query.filter(

        User.role_id == current_user.role_id,

        User.id != current_user.id

    ).all()


    return render_template(

        "dashboard/revenue.html",

        active_page="revenue",
        users=users
    )


@dashboard_bp.route("/analytics")
@login_required
def analytics():

    users = User.query.filter(

        User.role_id == current_user.role_id,

        User.id != current_user.id

    ).all()    

    return render_template(

        "dashboard/analytics.html",

        active_page="analytics",
        users=users
    )


@dashboard_bp.route("/workspace")
@login_required
def workspace():

    users = User.query.filter(

        User.role_id == current_user.role_id,

        User.id != current_user.id

    ).all()

    return render_template(

        "dashboard/workspace.html",

        active_page="workspace",
        users=users
    )


# =========================
# WORKSPACE PAGES
# =========================

@dashboard_bp.route(
    "/workspace/youtube-tracking"
)
@login_required
def youtube_tracking():

    channels = YoutubeChannel.query.all()

    tracking_rows = (

        YoutubeTracking.query

        .order_by(
            YoutubeTracking.id.desc()
        )

        .all()
    )

    return render_template(

        "dashboard/youtube_tracking.html",

        channels=channels,

        tracking_rows=tracking_rows
    )


@dashboard_bp.route(

    "/workspace/save-tracking-link",

    methods=["POST"]
)
@login_required
def save_tracking_link():

    video_url = request.form.get(
        "video_url"
    )

    if not video_url:

        return redirect(
            url_for(
                "dashboard.youtube_tracking"
            )
        )

    existing = YoutubeTracking.query.filter_by(
        video_url=video_url
    ).first()

    if existing:

        flash(
            "Already Exists",
            "warning"
        )

        return redirect(
            url_for(
                "dashboard.youtube_tracking"
            )
        )

    tracking = YoutubeTracking(

        video_url=video_url,

        video_title="Loading...",

        channel_name="Loading...",

        strip_name="Loading...",

        published_date="Loading..."
    )

    db.session.add(
        tracking
    )

    db.session.commit()

    thread = threading.Thread(

        target=background_tracking_scan,

        args=(

            current_app._get_current_object(),

            tracking.id,

            video_url
        ),

        daemon=True
    )

    thread.start()

    return redirect(
        url_for(
            "dashboard.youtube_tracking"
        )
    )


@dashboard_bp.route(

    "/workspace/delete-tracking-link",

    methods=["POST"]
)
@login_required
def delete_tracking_link():

    data = request.get_json()

    row_id = data.get(
        "id"
    )

    row = YoutubeTracking.query.get(
        row_id
    )

    if not row:

        return jsonify({

            "success": False
        })

    db.session.delete(
        row
    )

    db.session.commit()

    return jsonify({

        "success": True
    })


@dashboard_bp.route(

    "/workspace/edit-tracking-link",

    methods=["POST"]
)
@login_required
def edit_tracking_link():

    data = request.get_json()

    row_id = data.get(
        "id"
    )

    strip_name = data.get(
        "strip_name"
    )

    video_url = data.get(
        "video_url"
    )

    published_date = data.get(
        "published_date"
    )

    row = YoutubeTracking.query.get(
        row_id
    )

    if not row:

        return jsonify({

            "success": False
        })

    row.strip_name = strip_name

    row.video_url = video_url

    row.published_date = published_date

    db.session.commit()

    return jsonify({

        "success": True
    })

@dashboard_bp.route(
    "/workspace/export-tracking"
)
@login_required
def export_tracking():

    query = YoutubeTracking.query

    rows = query.all()

    output = StringIO()

    writer = csv.writer(
        output
    )

    writer.writerow([

        "Video Title",

        "Video URL",

        "Published Date",

        "Added Date"
    ])

    for row in rows:

        writer.writerow([

            row.video_title,

            row.video_url,

            row.published_date,

            row.created_at
        ])

    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={

            "Content-Disposition":
            "attachment; filename=youtube_tracking.csv"
        }
    )







@dashboard_bp.route(
    "/workspace/facebook-tracking"
)
@login_required
def facebook_tracking():

    return render_template(
        "dashboard/facebook_tracking.html"
    )







@dashboard_bp.route(
    "/workspace/yt-automation"
)
@login_required
def yt_automation():

    strip_results = (
        YoutubeStripResult.query
        .order_by(
            YoutubeStripResult.id.desc()
        )
        .all()
    )

    channels = (
        YoutubeChannel.query
        .order_by(
            YoutubeChannel.id.desc()
        )
        .all()
    )

    return render_template(

        "dashboard/yt_automation.html",

        strip_results=strip_results,

        channels=channels
    )

@dashboard_bp.route(
    "/workspace/fb-automation"
)
@login_required
def fb_automation():

    return render_template(
        "dashboard/fb_automation.html"
    )




def background_tracking_scan(

    app,

    tracking_id,

    video_url
):

    with app.app_context():

        try:

            tracking = YoutubeTracking.query.get(
                tracking_id
            )

            if not tracking:

                return

            scan_data = tracking_scan_youtube_video(
                video_url
            )

            from yt_dlp import YoutubeDL

            channel_url = ""

            with YoutubeDL({

                "quiet": True

            }) as ydl:

                info = ydl.extract_info(

                    video_url,

                    download=False
                )

                channel_id = info.get(
                    "channel_id"
                )

                if channel_id:

                    channel_url = (
                        f"https://www.youtube.com/channel/{channel_id}"
                    )

            print(
                scan_data
            )

            from yt_dlp import YoutubeDL

            publish_date = "-"

            try:

                with YoutubeDL({

                    "quiet": True

                }) as ydl:

                    info = ydl.extract_info(

                        video_url,

                        download=False
                    )

                    raw_date = info.get(
                        "upload_date",
                        ""
                    )

                    if len(raw_date) == 8:

                        publish_date = (

                            f"{raw_date[:4]}-"
                            f"{raw_date[4:6]}-"
                            f"{raw_date[6:]}"
                        )

                    else:

                        publish_date = "-"

            except Exception as error:

                print(
                    f"DATE ERROR: {error}"
                )

            results = scan_data.get(
                "results",
                []
            )

            print(
                f"OCR RESULTS = {results}"
            )

            tracking.channel_name = (
                scan_data.get(
                    "channel_name",
                    "Unknown"
                )
            )

            existing_channel = (
                YoutubeChannel.query.filter_by(
                    channel_name=tracking.channel_name
                ).first()
            )

            if not existing_channel:

                new_channel = YoutubeChannel(

                    channel_name=tracking.channel_name,

                    channel_url=channel_url,

                    is_active=True
                )

                db.session.add(
                    new_channel
                )

            tracking.video_title = (
                scan_data.get(
                    "video_title",
                    "Unknown"
                )
            )

            tracking.published_date = (
                publish_date
            )

            if results:

                tracking.strip_name = (

                    results[0].get(
                        "text",
                        "No Strip Found"
                    )
                )

            else:

                tracking.strip_name = (
                    "No Strip Found"
                )

            db.session.commit()

        except Exception as error:

            print(
                f"TRACKING OCR ERROR : {error}"
            )

            db.session.rollback()


            

@dashboard_bp.route(

    "/workspace/add-channel",

    methods=["POST"]
)
@login_required
def add_channel():

    channel_name = request.form.get(
        "channel_name"
    )

    channel_url = request.form.get(
        "channel_url"
    )

    if not channel_name or not channel_url:

        flash(

            "Channel name and URL required",

            "warning"
        )

        return redirect(

            url_for(
                "dashboard.yt_automation"
            )
        )

    existing_channel = YoutubeChannel.query.filter_by(

        channel_url=channel_url

    ).first()

    if existing_channel:

        flash(

            "Channel already exists",

            "warning"
        )

        return redirect(

            url_for(
                "dashboard.yt_automation"
            )
        )

    try:

        new_channel = YoutubeChannel(

            channel_name=channel_name,

            channel_url=channel_url,

            is_active=True
        )

        db.session.add(
            new_channel
        )

        db.session.commit()

        flash(

            "Channel Added",

            "success"
        )

    except Exception as error:

        db.session.rollback()

        print(error)

        flash(

            "Failed to add channel",

            "danger"
        )

    return redirect(

        url_for(
            "dashboard.yt_automation"
        )
    )


@dashboard_bp.route(

    "/workspace/run-channel-scan",

    methods=["POST"]
)
@login_required
def run_channel_scan():

    print(
        "\nRUN BUTTON CLICKED\n"
    )

    global SCAN_RUNNING

    if SCAN_RUNNING:

        flash(

            "Scan already running",

            "warning"
        )

        return redirect(

            url_for(
                "dashboard.yt_automation"
            )
        )

    channel_id = request.form.get(
        "channel_id"
    )

    video_count = int(

        request.form.get(
            "video_count",
            50
        )
    )

    if not channel_id:

        flash(

            "Select a channel",

            "warning"
        )

        return redirect(

            url_for(
                "dashboard.yt_automation"
            )
        )
    
    SCAN_RUNNING = True
    
    thread = threading.Thread(

        target=background_scan,

        args=(

            current_app._get_current_object(),

            channel_id,

            video_count
        ),

        daemon=True
    )

    thread.start()

    print(
        f"THREAD STARTED : {channel_id}"
    )

    flash(

        "Background scan started",

        "success"
    )

    return redirect(

        url_for(
            "dashboard.yt_automation"
        )
    )

@dashboard_bp.route(

    "/workspace/stop-channel-scan",

    methods=["POST"]
)
@login_required
def stop_channel_scan():

    global SCAN_RUNNING

    SCAN_RUNNING = False

    return jsonify({

        "success": True
    })



@dashboard_bp.route(
    "/workspace/scan-status"
)
@login_required
def scan_status():

    return jsonify({

        "running": SCAN_RUNNING
    })


@dashboard_bp.route(
    "/workspace/delete-strip-results",
    methods=["POST"]
)
@login_required
def delete_strip_results():

    data = request.get_json()

    ids = data.get(
        "ids",
        []
    )

    try:

        YoutubeStripResult.query.filter(

            YoutubeStripResult.id.in_(ids)

        ).delete(

            synchronize_session=False
        )

        db.session.commit()

        return jsonify({

            "success": True
        })

    except Exception as error:

        db.session.rollback()

        print(error)

        return jsonify({

            "success": False
        })

@dashboard_bp.route(
    "/workspace/update-strip-result",
    methods=["POST"]
)
@login_required
def update_strip_result():

    data = request.get_json()

    row_id = data.get(
        "id"
    )

    strip_name = data.get(
        "strip_name"
    )

    row = YoutubeStripResult.query.get(
        row_id
    )

    if not row:

        return jsonify({

            "success": False
        })

    row.strip_text = strip_name

    db.session.commit()

    return jsonify({

        "success": True
    })



@dashboard_bp.route(
    "/workspace/commercials"
)
@login_required
def commercials():

    return render_template(
        "dashboard/commercials.html"
    )

    
@dashboard_bp.route(
    "/workspace/commercials/add-channel",
    methods=["POST"]
)
@login_required
def add_commercial_channel():

    data = request.get_json()

    channel = CommercialChannel(

        channel_name=data["channel_name"],

        channel_url=data["channel_url"]
    )

    db.session.add(channel)

    db.session.commit()

    return jsonify({
        "success":True
    })

@dashboard_bp.route(
    "/workspace/commercials/add-client",
    methods=["POST"]
)
@login_required
def add_commercial_client():

    ad_name = request.form.get(
        "ad_name"
    )

    ad_type = request.form.get(
        "ad_type"
    )

    client_name = request.form.get(
        "client_name"
    )

    client_acquisition = request.form.get(
        "client_acquisition"
    )

    saved_images = []

    files = request.files.getlist(
        "sample_images"
    )

    upload_folder = os.path.join(

        current_app.static_folder,

        "uploads",

        "commercials"
    )

    os.makedirs(

        upload_folder,

        exist_ok=True
    )

    for file in files:

        if not file:

            continue

        filename = secure_filename(
            file.filename
        )

        timestamp = str(
            int(time.time())
        )

        filename = (
            f"{timestamp}_{filename}"
        )

        absolute_path = os.path.join(

            upload_folder,

            filename
        )

        file.save(
            absolute_path
        )

        saved_images.append(

            f"/static/uploads/commercials/{filename}"
        )

    client = CommercialClient(

        ad_name=ad_name,

        ad_type=ad_type,

        client_name=client_name,

        client_acquisition=client_acquisition,

        sample_images=json.dumps(
            saved_images
        )
    )

    db.session.add(
        client
    )

    db.session.commit()

    return jsonify({

        "success":True
    })

@dashboard_bp.route(
    "/workspace/commercials/clients"
)
@login_required
def get_commercial_clients():

    rows = CommercialClient.query.all()

    return jsonify([

        {

            "id":x.id,

            "ad_name":
            x.ad_name,

            "ad_type":
            x.ad_type,

            "client_name":
            x.client_name,

            "client_acquisition":
            x.client_acquisition
        }

        for x in rows
    ])

@dashboard_bp.route(
    "/workspace/commercials/channels"
)
@login_required
def get_commercial_channels():

    rows = CommercialChannel.query.all()

    return jsonify([

        {
            "id":x.id,
            "channel_name":x.channel_name,
            "channel_url":x.channel_url
        }

        for x in rows
    ])

@dashboard_bp.route(
    "/workspace/commercials/channel/<int:id>",
    methods=["DELETE"]
)
@login_required
def delete_commercial_channel(id):

    row = CommercialChannel.query.get(id)

    if row:

        db.session.delete(row)

        db.session.commit()

    return jsonify({
        "success":True
    })

@dashboard_bp.route(
    "/workspace/commercials/channel/<int:id>",
    methods=["PUT"]
)
@login_required
def update_commercial_channel(id):

    row = CommercialChannel.query.get_or_404(id)

    data = request.get_json()

    row.channel_name = data.get(
        "channel_name"
    )

    row.channel_url = data.get(
        "channel_url"
    )

    db.session.commit()

    return jsonify({
        "success":True
    })


@dashboard_bp.route(
    "/workspace/commercials/client/<int:id>",
    methods=["PUT"]
)
@login_required
def update_commercial_client(id):

    row = CommercialClient.query.get_or_404(
        id
    )

    ad_name = request.form.get(
        "ad_name"
    )

    ad_type = request.form.get(
        "ad_type"
    )

    client_name = request.form.get(
        "client_name"
    )

    client_acquisition = request.form.get(
        "client_acquisition"
    )

    row.ad_name = ad_name

    row.ad_type = ad_type

    row.client_name = client_name

    row.client_acquisition = client_acquisition

    db.session.commit()

    return jsonify({
        "success":True
    })

@dashboard_bp.route(
    "/workspace/commercials/client/<int:id>",
    methods=["DELETE"]
)
@login_required
def delete_commercial_client(id):

    row = CommercialClient.query.get(id)

    if row:

        db.session.delete(row)

        db.session.commit()

    return jsonify({
        "success":True
    })


def background_commercial_scan(

    app,

    channel_id,

    video_count
):

    global COMMERCIAL_SCAN_RUNNING

    with app.app_context():

        try:

            print("\n")
            print("=" * 60)
            print("COMMERCIAL SCAN STARTED")
            print("=" * 60)

            channel = CommercialChannel.query.get(
                channel_id
            )

            if not channel:

                print(
                    "CHANNEL NOT FOUND"
                )

                return

            videos = get_latest_videos(

                channel.channel_url,

                video_count
            )

            print(
                f"VIDEOS FOUND : {len(videos)}"
            )

            for video in videos:

                if not COMMERCIAL_SCAN_RUNNING:

                    print(
                        "SCAN STOPPED"
                    )

                    break

                video_url = video["url"]

                print(
                    f"\nVIDEO : {video_url}"
                )

                try:

                    video_file = download_video(

                        video_url,

                        "temp/commercials/videos"
                    )

                    print(
                        f"DOWNLOADED : {video_file}"
                    )

                    frame_folder = os.path.join(

                        "temp",

                        "commercials",

                        "frames",

                        video["video_id"]
                    )

                    extract_frames(

                        video_file,

                        frame_folder
                    )

                    frame_paths = []

                    for file in os.listdir(
                        frame_folder
                    ):

                        if file.endswith(
                            ".jpg"
                        ):

                            frame_paths.append(

                                os.path.join(

                                    frame_folder,

                                    file
                                )
                            )

                    print(
                        f"FRAMES : {len(frame_paths)}"
                    )

                    process_frames(

                        frame_paths,

                        channel.channel_name,

                        video_url,

                        "",

                        0
                    )

                    print(
                        "OCR COMPLETED"
                    )

                except Exception as error:

                    print(
                        f"OCR ERROR : {error}"
                    )

        except Exception as error:

            print(error)

        finally:

            COMMERCIAL_SCAN_RUNNING = False

            print("\n")
            print("=" * 60)
            print("COMMERCIAL SCAN FINISHED")
            print("=" * 60)

@dashboard_bp.route(
    "/workspace/commercials/run-scan",
    methods=["POST"]
)
@login_required
def run_commercial_scan():

    global COMMERCIAL_SCAN_RUNNING

    if COMMERCIAL_SCAN_RUNNING:

        return jsonify({
            "success":False,
            "message":"Scan already running"
        })

    data = request.get_json()

    channel_id = data.get(
        "channel_id"
    )

    video_count = int(
        data.get(
            "video_count",
            10
        )
    )

    channel = CommercialChannel.query.get(
        channel_id
    )

    if not channel:

        return jsonify({
            "success":False
        })

    COMMERCIAL_SCAN_RUNNING = True

    thread = threading.Thread(

        target=background_commercial_scan,

        args=(

            current_app._get_current_object(),

            channel.id,

            video_count
        ),

        daemon=True
    )

    thread.start()

    return jsonify({
        "success":True
    })

@dashboard_bp.route(
    "/workspace/commercials/stop-scan",
    methods=["POST"]
)
@login_required
def stop_commercial_scan():

    global COMMERCIAL_SCAN_RUNNING

    COMMERCIAL_SCAN_RUNNING = False

    return jsonify({

        "success": True
    })



            
