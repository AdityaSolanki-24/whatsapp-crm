import os
import logging
from werkzeug.utils import secure_filename
from database.db import db
from models.media_file import MediaFile
from utils.helpers import generate_unique_filename, get_upload_path
from utils.validators import allowed_image_file

logger = logging.getLogger(__name__)

MEDIA_SUBFOLDER = "campaigns"


class MediaService:

    def get_all(self):
        return MediaFile.query.order_by(MediaFile.uploaded_at.desc()).all()

    def get_by_id(self, media_id: int) -> MediaFile:
        return MediaFile.query.get(media_id)

    def save_upload(self, file_storage) -> dict:
        """
        Save an uploaded image file and record it in the DB.
        Returns dict with success flag and media record or error.
        """
        if not file_storage or not file_storage.filename:
            return {"success": False, "error": "No file provided"}

        original_name = secure_filename(file_storage.filename)
        if not allowed_image_file(original_name):
            return {"success": False, "error": "File type not allowed. Use PNG, JPG, JPEG, GIF, or WEBP."}

        unique_name = generate_unique_filename(original_name)
        upload_dir = get_upload_path(MEDIA_SUBFOLDER)
        os.makedirs(upload_dir, exist_ok=True)

        full_path = os.path.join(upload_dir, unique_name)
        try:
            file_storage.save(full_path)
        except Exception as e:
            logger.exception(f"File save error: {e}")
            return {"success": False, "error": f"Could not save file: {e}"}

        file_size = os.path.getsize(full_path)
        relative_path = f"static/uploads/{MEDIA_SUBFOLDER}/{unique_name}"

        media = MediaFile(
            filename=unique_name,
            original_filename=original_name,
            file_path=relative_path,
            file_size=file_size,
            mime_type=file_storage.content_type,
        )
        db.session.add(media)
        db.session.commit()

        return {"success": True, "media": media}

    def delete(self, media_id: int) -> dict:
        media = MediaFile.query.get(media_id)
        if not media:
            return {"success": False, "error": "Media not found"}

        from flask import current_app
        full_path = os.path.join(current_app.root_path, media.file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception as e:
                logger.warning(f"Could not delete file {full_path}: {e}")

        db.session.delete(media)
        db.session.commit()
        return {"success": True}
