from database.db import db
from models.system import AuditLog, SystemLog
from flask import request
from flask_login import current_user

class SystemService:
    @staticmethod
    def log_audit(action: str, details: str = None):
        admin_id = current_user.id if current_user and current_user.is_authenticated else None
        ip_address = request.remote_addr if request else None
        
        log = AuditLog(admin_id=admin_id, action=action, details=details, ip_address=ip_address)
        db.session.add(log)
        db.session.commit()

    @staticmethod
    def log_error(module: str, message: str, traceback: str = None):
        """Centralized DB error logging for the UI Monitor."""
        log = SystemLog(level="ERROR", module=module, message=message, traceback=traceback)
        db.session.add(log)
        db.session.commit()