from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from services.media_service import MediaService

media_bp = Blueprint("media", __name__, url_prefix="/media")
media_service = MediaService()


@media_bp.route("/")
@login_required
def index():
    files = media_service.get_all()
    return render_template("media/media.html", files=files)


@media_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "image_file" not in request.files:
            flash("No file selected.", "warning")
            return redirect(request.url)

        file = request.files["image_file"]
        if not file or not file.filename:
            flash("No file selected.", "warning")
            return redirect(request.url)

        result = media_service.save_upload(file)
        if result["success"]:
            flash(f"Image '{result['media'].original_filename}' uploaded successfully.", "success")
            return redirect(url_for("media.index"))
        else:
            flash(result["error"], "danger")
            return redirect(request.url)

    return render_template("media/media_upload.html")


@media_bp.route("/<int:media_id>/delete", methods=["POST"])
@login_required
def delete(media_id):
    result = media_service.delete(media_id)
    if result["success"]:
        flash("Image deleted.", "success")
    else:
        flash(result.get("error", "Delete failed."), "danger")
    return redirect(url_for("media.index"))


@media_bp.route("/api/list")
@login_required
def api_list():
    """JSON endpoint to list media files for campaign image picker."""
    files = media_service.get_all()
    return jsonify([
        {
            "id": f.id,
            "filename": f.filename,
            "original_filename": f.original_filename,
            "file_path": f.file_path,
            "file_size": f.file_size,
        }
        for f in files
    ])
