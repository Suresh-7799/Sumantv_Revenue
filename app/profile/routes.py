@profile_bp.route("/settings")
@login_required
def settings():
    return render_template("profile/settings.html")
