from database.db import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    admin = db.relationship("Admin", backref="audit_logs")

class SystemLog(db.Model):
    __tablename__ = "system_logs"

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False, index=True) # ERROR, WARNING, INFO
    module = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    traceback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class BackgroundJob(db.Model):
    __tablename__ = "background_jobs"

    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.String(20), default="pending", index=True) # pending, running, completed, failed
    payload = db.Column(db.Text, nullable=True)
    result = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

class BackupRecord(db.Model):
    __tablename__ = "backup_records"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    backup_type = db.Column(db.String(50), nullable=False) # database, media, full
    file_size = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="completed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)