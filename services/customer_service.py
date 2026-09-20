import logging
from database.db import db
from models.customer import Customer
from utils.validators import validate_phone, validate_email
from utils.helpers import format_phone_number

logger = logging.getLogger(__name__)


class CustomerService:

    def get_all(self, page=1, per_page=25, search=None, search_by="name"):
        query = Customer.query
        if search:
            search = search.strip()
            if search_by == "phone":
                query = query.filter(Customer.phone.ilike(f"%{search}%"))
            elif search_by == "customer_id":
                query = query.filter(Customer.customer_id.ilike(f"%{search}%"))
            else:
                query = query.filter(Customer.name.ilike(f"%{search}%"))
        query = query.order_by(Customer.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_by_id(self, customer_id: int) -> Customer:
        return Customer.query.get(customer_id)

    def create(self, data: dict) -> dict:
        phone_raw = data.get("phone", "")
        valid, phone_or_err = validate_phone(phone_raw)
        if not valid:
            return {"success": False, "error": phone_or_err}

        phone = phone_or_err
        if Customer.query.filter_by(phone=phone).first():
            return {"success": False, "error": f"Phone number {phone} already exists"}

        cid = data.get("customer_id", "").strip()
        if Customer.query.filter_by(customer_id=cid).first():
            return {"success": False, "error": f"Customer ID '{cid}' already exists"}

        email_raw = data.get("email", "")
        email = (email_raw or "").strip()
        if email and not validate_email(email):
            return {"success": False, "error": "Invalid email address"}


        customer = Customer(
            customer_id=cid,
            name=data.get("name", "").strip(),
            email=email,
            phone=phone,
            orders=int(data.get("orders", 0) or 0),
            status=data.get("status", "active"),
        )
        db.session.add(customer)
        db.session.commit()
        return {"success": True, "customer": customer}

    def update(self, customer_id: int, data: dict) -> dict:
        customer = Customer.query.get(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}

        phone_raw = data.get("phone", customer.phone)
        valid, phone_or_err = validate_phone(phone_raw)
        if not valid:
            return {"success": False, "error": phone_or_err}

        phone = phone_or_err
        existing = Customer.query.filter_by(phone=phone).first()
        if existing and existing.id != customer_id:
            return {"success": False, "error": f"Phone {phone} is used by another customer"}

        cid = data.get("customer_id", customer.customer_id).strip()
        existing_cid = Customer.query.filter_by(customer_id=cid).first()
        if existing_cid and existing_cid.id != customer_id:
            return {"success": False, "error": f"Customer ID '{cid}' is used by another customer"}

        email = data.get("email", customer.email or "").strip()
        if email and not validate_email(email):
            return {"success": False, "error": "Invalid email address"}

        customer.customer_id = cid
        customer.name = data.get("name", customer.name).strip()
        customer.email = email
        customer.phone = phone
        customer.orders = int(data.get("orders", customer.orders) or 0)
        customer.status = data.get("status", customer.status)
        db.session.commit()
        return {"success": True, "customer": customer}

    def delete(self, customer_id: int) -> bool:
        customer = Customer.query.get(customer_id)
        if not customer:
            return False
        db.session.delete(customer)
        db.session.commit()
        return True

    def delete_many(self, customer_ids: list[int]) -> dict:
        if not customer_ids:
            return {"success": False, "error": "No customers selected"}

        # Remove duplicates while preserving order for stable UX.
        seen = set()
        ids: list[int] = []
        for cid in customer_ids:
            try:
                cid_int = int(cid)
            except (TypeError, ValueError):
                continue
            if cid_int not in seen:
                seen.add(cid_int)
                ids.append(cid_int)

        if not ids:
            return {"success": False, "error": "No valid customers selected"}

        existing = Customer.query.filter(Customer.id.in_(ids)).all()
        existing_ids = {c.id for c in existing}

        deleted_count = 0
        for c in existing:
            db.session.delete(c)
            deleted_count += 1

        db.session.commit()

        not_found_count = len(ids) - len(existing_ids)
        return {
            "success": True,
            "deleted": deleted_count,
            "not_found": not_found_count,
            "total_requested": len(ids),
        }


    def get_active_customers(self):
        return Customer.query.filter_by(status="active").all()
