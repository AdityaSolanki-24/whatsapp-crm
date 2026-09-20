from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from models.system import AuditLog, SystemLog, BackgroundJob, BackupRecord
from services.backup_service import BackupService
from database.db import db
import psutil
import os

system_bp = Blueprint("system", __name__, url_prefix="/system")

@system_bp.route("/audit-logs")
@login_required
def audit_logs():
    page = request.args.get("page", 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template("system/audit_logs.html", logs=logs)

@system_bp.route("/error-logs")
@login_required
def error_logs():
    page = request.args.get("page", 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template("system/error_logs.html", logs=logs)

@system_bp.route("/queue")
@login_required
def job_queue():
    page = request.args.get("page", 1, type=int)
    jobs = BackgroundJob.query.order_by(BackgroundJob.created_at.desc()).paginate(page=page, per_page=30, error_out=False)
    return render_template("system/queue.html", jobs=jobs)

@system_bp.route("/health")
@login_required
def health_monitor():
    # Storage Usage
    disk = psutil.disk_usage(os.getcwd())
    storage = {
        "total": disk.total // (2**30),
        "used": disk.used // (2**30),
        "free": disk.free // (2**30),
        "percent": disk.percent
    }
    
    # Database check
    db_status = "Healthy"
    try:
        db.session.execute(db.text('SELECT 1'))
    except Exception:
        db_status = "Disconnected/Error"
        
    return render_template("system/health.html", storage=storage, db_status=db_status)

@system_bp.route("/backups", methods=["GET", "POST"])
@login_required
def backups():
    if request.method == "POST":
        result = BackupService().create_database_backup()
        if result["success"]:
            flash("Backup created successfully.", "success")
        else:
            flash(f"Backup failed: {result.get('error')}", "danger")
        return redirect(url_for('system.backups'))
        
    records = BackupRecord.query.order_by(BackupRecord.created_at.desc()).all()
    return render_template("system/backups.html", backups=records)