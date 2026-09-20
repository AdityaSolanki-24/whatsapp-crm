"""
Tests for authentication routes and services.
Run with: pytest tests/test_auth.py -v
"""
import pytest
from app import create_app
from database.db import db as _db
from models.admin import Admin


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
    })
    with app.app_context():
        _db.create_all()
        # Create test admin
        admin = Admin(username="testadmin")
        admin.set_password("testpass123")
        _db.session.add(admin)
        _db.session.commit()
    yield app
    with app.app_context():
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Logged-in test client."""
    client.post("/login", data={"username": "testadmin", "password": "testpass123"})
    return client


class TestLoginPage:
    def test_login_page_loads(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Admin Login" in resp.data or b"Sign In" in resp.data

    def test_login_success_redirects(self, client):
        resp = client.post(
            "/login",
            data={"username": "testadmin", "password": "testpass123"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"Dashboard" in resp.data or b"Welcome" in resp.data

    def test_login_wrong_password(self, client):
        resp = client.post(
            "/login",
            data={"username": "testadmin", "password": "wrongpass"},
            follow_redirects=True,
        )
        assert b"Invalid" in resp.data

    def test_login_unknown_user(self, client):
        resp = client.post(
            "/login",
            data={"username": "nobody", "password": "whatever"},
            follow_redirects=True,
        )
        assert b"Invalid" in resp.data

    def test_dashboard_requires_login(self, client):
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code in (302, 308)

    def test_logout(self, auth_client):
        resp = auth_client.get("/logout", follow_redirects=True)
        assert resp.status_code == 200


class TestAdminModel:
    def test_password_hashing(self, app):
        with app.app_context():
            admin = Admin(username="hashtest")
            admin.set_password("securepass")
            assert admin.password_hash != "securepass"
            assert admin.check_password("securepass") is True
            assert admin.check_password("wrongpass") is False

    def test_admin_repr(self, app):
        with app.app_context():
            admin = Admin(username="reprtest")
            assert "reprtest" in repr(admin)
