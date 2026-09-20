import logging
from database.db import db
from models.admin import Admin

logger = logging.getLogger(__name__)


class AuthService:

    def authenticate(self, username: str, password: str):
        """Return Admin if credentials are valid, else None."""
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            return admin
        return None

    def create_admin(self, username: str, password: str) -> Admin:
        """Create a new admin account."""
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        logger.info(f"Admin '{username}' created.")
        return admin

    def admin_exists(self) -> bool:
        return Admin.query.count() > 0

    def change_password(self, admin_id: int, new_password: str) -> bool:
        admin = Admin.query.get(admin_id)
        if not admin:
            return False
        admin.set_password(new_password)
        db.session.commit()
        return True
