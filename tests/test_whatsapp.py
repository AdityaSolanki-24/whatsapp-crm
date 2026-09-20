"""
Tests for WhatsApp service layer.
Run with: pytest tests/test_whatsapp.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from database.db import db as _db
from models.settings import Settings


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
        s = Settings(
            whatsapp_phone_id="123456789",
            whatsapp_access_token="test_token_abc",
        )
        _db.session.add(s)
        _db.session.commit()
    yield app
    with app.app_context():
        _db.drop_all()


class TestWhatsAppService:

    def test_send_text_success(self, app):
        with app.app_context():
            from services.whatsapp import WhatsAppService
            wa = WhatsAppService()

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "messaging_product": "whatsapp",
                "contacts": [{"input": "919876543210", "wa_id": "919876543210"}],
                "messages": [{"id": "wamid.test123"}],
            }

            with patch("requests.post", return_value=mock_response):
                result = wa.send_text_message("919876543210", "Hello World")

            assert result["success"] is True
            assert result["message_id"] == "wamid.test123"

    def test_send_text_api_error(self, app):
        with app.app_context():
            from services.whatsapp import WhatsAppService
            wa = WhatsAppService()

            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": {
                    "message": "Invalid phone number",
                    "type": "OAuthException",
                    "code": 100,
                }
            }

            with patch("requests.post", return_value=mock_response):
                result = wa.send_text_message("badphone", "Hello")

            assert result["success"] is False
            assert "Invalid phone number" in result["error"]

    def test_send_image_success(self, app):
        with app.app_context():
            from services.whatsapp import WhatsAppService
            wa = WhatsAppService()

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "messages": [{"id": "wamid.imgtest"}],
            }

            with patch("requests.post", return_value=mock_response):
                result = wa.send_image_message(
                    to="919876543210",
                    image_url="https://example.com/image.jpg",
                    caption="Check this out!",
                )

            assert result["success"] is True
            assert result["message_id"] == "wamid.imgtest"

    def test_send_without_credentials(self, app):
        with app.app_context():
            from services.whatsapp import WhatsAppService
            wa = WhatsAppService()
            wa.phone_id = ""
            wa.access_token = ""
            result = wa.send_text_message("919876543210", "Hello")
            assert result["success"] is False
            assert "credentials" in result["error"].lower()

    def test_send_timeout(self, app):
        import requests as req_lib
        with app.app_context():
            from services.whatsapp import WhatsAppService
            wa = WhatsAppService()
            with patch("requests.post", side_effect=req_lib.exceptions.Timeout):
                result = wa.send_text_message("919876543210", "Hello")
            assert result["success"] is False
            assert "timed out" in result["error"].lower()

    def test_send_connection_error(self, app):
        import requests as req_lib
        with app.app_context():
            from services.whatsapp import WhatsAppService
            wa = WhatsAppService()
            with patch("requests.post", side_effect=req_lib.exceptions.ConnectionError):
                result = wa.send_text_message("919876543210", "Hello")
            assert result["success"] is False
            assert "connection" in result["error"].lower()

    def test_test_connection_success(self, app):
        with app.app_context():
            from services.whatsapp import WhatsAppService
            wa = WhatsAppService()

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "123456789",
                "display_phone_number": "+91 98765 43210",
                "quality_rating": "GREEN",
            }

            with patch("requests.get", return_value=mock_response):
                result = wa.test_connection()

            assert result["success"] is True

    def test_test_connection_invalid_token(self, app):
        with app.app_context():
            from services.whatsapp import WhatsAppService
            wa = WhatsAppService()

            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                "error": {"message": "Invalid OAuth access token", "code": 190}
            }

            with patch("requests.get", return_value=mock_response):
                result = wa.test_connection()

            assert result["success"] is False


class TestMessageRendering:
    def test_render_all_variables(self, app):
        with app.app_context():
            from utils.helpers import render_message
            template = "Hi {name}! ID={customer_id} Email={email} Orders={orders} Status={status}"
            data = {
                "name": "Rahul",
                "customer_id": "C001",
                "email": "rahul@test.com",
                "orders": "5",
                "status": "active",
            }
            result = render_message(template, data)
            assert "Rahul" in result
            assert "C001" in result
            assert "rahul@test.com" in result
            assert "5" in result
            assert "active" in result

    def test_render_missing_variable_empty(self, app):
        with app.app_context():
            from utils.helpers import render_message
            result = render_message("Hello {name}!", {})
            assert "Hello " in result

    def test_render_multiline_message(self, app):
        with app.app_context():
            from utils.helpers import render_message
            template = "Line 1: {name}\nLine 2: {orders} orders"
            data = {"name": "Alice", "orders": "3"}
            result = render_message(template, data)
            assert "Alice" in result
            assert "3" in result
            assert "\n" in result
