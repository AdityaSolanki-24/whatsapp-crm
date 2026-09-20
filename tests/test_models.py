from models.admin import Admin
from models.system import AuditLog
from database.db import db

def test_admin_password_hashing(app):
    admin = Admin(username="securitytest")
    admin.set_password("mypassword")
    
    assert admin.check_password("mypassword") is True
    assert admin.check_password("wrongpassword") is False
    assert admin.password_hash != "mypassword"