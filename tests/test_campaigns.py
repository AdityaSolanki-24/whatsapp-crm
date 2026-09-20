"""
Tests for campaign routes and campaign service.
Run with: pytest tests/test_campaigns.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from database.db import db as _db
from models.admin import Admin
from models.customer import Customer
from models.campaign import Campaign
from models.campaign_log import CampaignLog


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
        "CAMPAIGN_DELAY_SECONDS": 0,
    })
    with app.app_context():
        _db.create_all()
        admin = Admin(username="testadmin")
        admin.set_password("testpass")
        _db.session.add(admin)
        # Add test customers
        for i in range(3):
            _db.session.add(Customer(
                customer_id=f"T{i:03d}",
                name=f"Test Customer {i}",
                phone=f"91900000000{i}",
                orders=i,
                status="active",
            ))
        _db.session.commit()
    yield app
    with app.app_context():
        _db.drop_all()


@pytest.fixture
def client(app):
    c = app.test_client()
    c.post("/login", data={"username": "testadmin", "password": "testpass"})
    return c


@pytest.fixture(autouse=True)
def clean_campaigns(app):
    with app.app_context():
        CampaignLog.query.delete()
        Campaign.query.delete()
        _db.session.commit()
    yield


class TestCampaignCRUD:
    def test_campaign_list(self, client):
        resp = client.get("/campaigns/")
        assert resp.status_code == 200

    def test_create_campaign_get(self, client):
        resp = client.get("/campaigns/create")
        assert resp.status_code == 200

    def test_create_campaign_post(self, client, app):
        resp = client.post(
            "/campaigns/create",
            data={
                "title": "Test Campaign",
                "message": "Hello {name}!",
                "image_path": "",
                "target": "all",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        with app.app_context():
            c = Campaign.query.filter_by(title="Test Campaign").first()
            assert c is not None
            assert c.message == "Hello {name}!"

    def test_view_campaign(self, client, app):
        with app.app_context():
            c = Campaign(title="View Me", message="Hi!", status="draft")
            _db.session.add(c)
            _db.session.commit()
            cid = c.id
        resp = client.get(f"/campaigns/{cid}")
        assert resp.status_code == 200

    def test_delete_campaign(self, client, app):
        with app.app_context():
            c = Campaign(title="Delete Me", message="Bye!", status="draft")
            _db.session.add(c)
            _db.session.commit()
            cid = c.id
        resp = client.post(f"/campaigns/{cid}/delete", follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            assert Campaign.query.get(cid) is None

    def test_campaign_history(self, client, app):
        with app.app_context():
            c = Campaign(
                title="History Campaign", message="Hi!",
                status="completed", total_customers=2, sent_count=2,
            )
            _db.session.add(c)
            _db.session.commit()
            cid = c.id
            log = CampaignLog(campaign_id=cid, phone="919000000000", status="sent")
            _db.session.add(log)
            _db.session.commit()
        resp = client.get(f"/campaigns/{cid}/history")
        assert resp.status_code == 200
        assert b"919000000000" in resp.data


class TestCampaignSend:
    @patch("services.campaign_service.WhatsAppService")
    def test_send_to_all_customers(self, mock_wa_class, client, app):
        mock_wa = MagicMock()
        mock_wa.send_text_message.return_value = {"success": True, "message_id": "abc123"}
        mock_wa.send_image_message.return_value = {"success": True, "message_id": "abc123"}
        mock_wa_class.return_value = mock_wa

        with app.app_context():
            c = Campaign(title="Send All", message="Hi {name}!", status="draft")
            _db.session.add(c)
            _db.session.commit()
            cid = c.id

        resp = client.post(
            f"/campaigns/{cid}/send",
            data={"target": "all"},
            follow_redirects=True,
        )
        assert resp.status_code == 200

        with app.app_context():
            updated = Campaign.query.get(cid)
            assert updated.status == "completed"
            assert updated.total_customers >= 3
            assert updated.sent_count >= 3

    @patch("services.campaign_service.WhatsAppService")
    def test_send_tracks_failures(self, mock_wa_class, client, app):
        mock_wa = MagicMock()
        mock_wa.send_text_message.return_value = {"success": False, "error": "Rate limit"}
        mock_wa_class.return_value = mock_wa

        with app.app_context():
            c = Campaign(title="Fail Campaign", message="Hi!", status="draft")
            _db.session.add(c)
            _db.session.commit()
            cid = c.id

        client.post(
            f"/campaigns/{cid}/send",
            data={"target": "all"},
            follow_redirects=True,
        )

        with app.app_context():
            updated = Campaign.query.get(cid)
            assert updated.failed_count == updated.total_customers
            logs = CampaignLog.query.filter_by(campaign_id=cid, status="failed").all()
            assert len(logs) == updated.total_customers


class TestCampaignModel:
    def test_success_rate_zero_customers(self, app):
        with app.app_context():
            c = Campaign(title="Empty", message="Hi", total_customers=0)
            assert c.success_rate == 0

    def test_success_rate_calculation(self, app):
        with app.app_context():
            c = Campaign(
                title="Rate Test", message="Hi",
                total_customers=10, sent_count=8
            )
            assert c.success_rate == 80.0

    def test_campaign_to_dict(self, app):
        with app.app_context():
            c = Campaign(title="Dict Test", message="Hello", status="draft")
            d = c.to_dict()
            assert d["title"] == "Dict Test"
            assert "success_rate" in d
            assert "status" in d
