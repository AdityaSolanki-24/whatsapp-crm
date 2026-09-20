from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from forms.settings_form import SettingsForm
from models.settings import Settings
from services.whatsapp import WhatsAppService
from database.db import db

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    settings = Settings.get_settings()
    form = SettingsForm(obj=settings)

    if form.validate_on_submit():
        settings.whatsapp_phone_id = form.whatsapp_phone_id.data.strip()
        settings.whatsapp_access_token = form.whatsapp_access_token.data.strip()
        db.session.commit()
        flash("Settings saved successfully.", "success")
        return redirect(url_for("settings.index"))

    return render_template("settings/settings.html", form=form, settings=settings)


@settings_bp.route("/test-connection", methods=["POST"])
@login_required
def test_connection():
    """AJAX endpoint to test WhatsApp credentials."""
    wa = WhatsAppService()
    result = wa.test_connection()
    return jsonify(result)
