"""
Tests for customer routes and CSV import.
Run with: pytest tests/test_customers.py -v
"""
import io
import pytest
from app import create_app
from database.db import db as _db
from models.admin import Admin
from models.customer import Customer


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
        admin = Admin(username="testadmin")
        admin.set_password("testpass")
        _db.session.add(admin)
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
def clean_customers(app):
    with app.app_context():
        Customer.query.delete()
        _db.session.commit()
    yield


def make_csv(rows: list[str]) -> io.BytesIO:
    header = "customer_id,name,email,phone,orders,status\n"
    content = header + "\n".join(rows)
    return io.BytesIO(content.encode("utf-8"))


class TestCustomerCRUD:
    def test_customer_list_empty(self, client):
        resp = client.get("/customers/")
        assert resp.status_code == 200

    def test_add_customer_get(self, client):
        resp = client.get("/customers/add")
        assert resp.status_code == 200

    def test_add_customer_post(self, client, app):
        resp = client.post(
            "/customers/add",
            data={
                "customer_id": "C001",
                "name": "Test User",
                "phone": "919876543210",
                "email": "test@example.com",
                "orders": "3",
                "status": "active",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        with app.app_context():
            cust = Customer.query.filter_by(customer_id="C001").first()
            assert cust is not None
            assert cust.name == "Test User"
            assert cust.phone == "919876543210"

    def test_add_duplicate_phone(self, client, app):
        client.post(
            "/customers/add",
            data={
                "customer_id": "C002",
                "name": "User A",
                "phone": "911111111111",
                "orders": "0",
                "status": "active",
            },
        )
        resp = client.post(
            "/customers/add",
            data={
                "customer_id": "C003",
                "name": "User B",
                "phone": "911111111111",
                "orders": "0",
                "status": "active",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        with app.app_context():
            count = Customer.query.filter_by(phone="911111111111").count()
            assert count == 1

    def test_edit_customer(self, client, app):
        client.post(
            "/customers/add",
            data={
                "customer_id": "C004",
                "name": "Edit Me",
                "phone": "912222222222",
                "orders": "1",
                "status": "active",
            },
        )
        with app.app_context():
            cust = Customer.query.filter_by(customer_id="C004").first()
            cid = cust.id

        resp = client.post(
            f"/customers/{cid}/edit",
            data={
                "customer_id": "C004",
                "name": "Edited Name",
                "phone": "912222222222",
                "email": "",
                "orders": "5",
                "status": "inactive",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        with app.app_context():
            updated = Customer.query.get(cid)
            assert updated.name == "Edited Name"
            assert updated.orders == 5
            assert updated.status == "inactive"

    def test_delete_customer(self, client, app):
        client.post(
            "/customers/add",
            data={
                "customer_id": "C005",
                "name": "Delete Me",
                "phone": "913333333333",
                "orders": "0",
                "status": "active",
            },
        )
        with app.app_context():
            cust = Customer.query.filter_by(customer_id="C005").first()
            cid = cust.id

        resp = client.post(f"/customers/{cid}/delete", follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            assert Customer.query.get(cid) is None

    def test_bulk_delete_customers(self, client, app):
        client.post(
            "/customers/add",
            data={
                "customer_id": "C006",
                "name": "Bulk A",
                "phone": "914444444444",
                "orders": "0",
                "status": "active",
            },
        )
        client.post(
            "/customers/add",
            data={
                "customer_id": "C007",
                "name": "Bulk B",
                "phone": "915555555555",
                "orders": "0",
                "status": "active",
            },
        )

        with app.app_context():
            c1 = Customer.query.filter_by(customer_id="C006").first()
            c2 = Customer.query.filter_by(customer_id="C007").first()
            cid1, cid2 = c1.id, c2.id
            assert Customer.query.get(cid1) is not None
            assert Customer.query.get(cid2) is not None

        resp = client.post(
            "/customers/delete_selected",
            data={
                "customer_ids": [str(cid1), str(cid2)],
                "search_by": "name",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200

        with app.app_context():
            assert Customer.query.get(cid1) is None
            assert Customer.query.get(cid2) is None

    def test_bulk_delete_no_selection(self, client):
        resp = client.post(
            "/customers/delete_selected",
            data={"customer_ids": [], "search_by": "name"},
            follow_redirects=True,
        )
        assert resp.status_code == 200



class TestCSVImport:
    def test_import_valid_csv(self, client, app):
        csv_data = make_csv([
            "C010,Alice Smith,alice@example.com,919000000001,5,active",
            "C011,Bob Jones,bob@example.com,919000000002,2,active",
        ])
        resp = client.post(
            "/customers/import",
            data={"csv_file": (csv_data, "customers.csv")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200
        with app.app_context():
            assert Customer.query.filter_by(customer_id="C010").first() is not None
            assert Customer.query.filter_by(customer_id="C011").first() is not None

    def test_import_skips_duplicates(self, client, app):
        csv_data = make_csv([
            "C020,Charlie,charlie@example.com,919000000010,1,active",
        ])
        client.post(
            "/customers/import",
            data={"csv_file": (csv_data, "c.csv")},
            content_type="multipart/form-data",
        )
        csv_data2 = make_csv([
            "C020,Charlie Again,charlie2@example.com,919000000010,2,active",
        ])
        client.post(
            "/customers/import",
            data={"csv_file": (csv_data2, "c2.csv")},
            content_type="multipart/form-data",
        )
        with app.app_context():
            count = Customer.query.filter_by(phone="919000000010").count()
            assert count == 1

    def test_import_invalid_phone_skipped(self, client, app):
        csv_data = make_csv([
            "C030,Invalid Phone,x@x.com,NOTAPHONE,0,active",
        ])
        client.post(
            "/customers/import",
            data={"csv_file": (csv_data, "bad.csv")},
            content_type="multipart/form-data",
        )
        with app.app_context():
            assert Customer.query.filter_by(customer_id="C030").first() is None

    def test_import_missing_required_column(self, client):
        bad_csv = io.BytesIO(b"name,email\nAlice,alice@x.com\n")
        resp = client.post(
            "/customers/import",
            data={"csv_file": (bad_csv, "bad.csv")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200


class TestCustomerSearch:
    def test_search_by_name(self, client, app):
        with app.app_context():
            _db.session.add(Customer(
                customer_id="S001", name="Searchable Person",
                phone="919100000001", orders=0, status="active"
            ))
            _db.session.commit()
        resp = client.get("/customers/?search=Searchable&search_by=name")
        assert resp.status_code == 200
        assert b"Searchable" in resp.data

    def test_search_by_phone(self, client, app):
        with app.app_context():
            _db.session.add(Customer(
                customer_id="S002", name="Phone Search",
                phone="919200000002", orders=0, status="active"
            ))
            _db.session.commit()
        resp = client.get("/customers/?search=919200000002&search_by=phone")
        assert resp.status_code == 200
        assert b"919200000002" in resp.data
