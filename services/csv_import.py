import pandas as pd
import logging
from typing import Optional
from database.db import db
from models.customer import Customer
from utils.validators import validate_phone, validate_email
from utils.helpers import format_phone_number
from utils.constants import CSV_REQUIRED_COLUMNS

logger = logging.getLogger(__name__)


class CSVImportService:

    def import_csv(self, filepath: str) -> dict:
        """
        Import customers from a CSV file.
        Returns summary with counts of created, skipped, and errors.
        """
        result = {
            "success": False,
            "created": 0,
            "skipped_duplicate": 0,
            "skipped_invalid": 0,
            "errors": [],
            "total_rows": 0,
        }

        try:
            df = pd.read_csv(filepath, dtype=str)
        except Exception as e:
            result["errors"].append(f"Could not read CSV file: {e}")
            return result

        df.columns = [col.strip().lower() for col in df.columns]

        missing = CSV_REQUIRED_COLUMNS - set(df.columns)
        if missing:
            result["errors"].append(
                f"Missing required columns: {', '.join(missing)}. "
                f"Required: customer_id, name, phone"
            )
            return result

        df = df.fillna("")
        result["total_rows"] = len(df)

        for idx, row in df.iterrows():
            row_num = idx + 2  # 1-indexed + header
            customer_id = str(row.get("customer_id", "")).strip()
            name = str(row.get("name", "")).strip()
            phone_raw = str(row.get("phone", "")).strip()
            email = str(row.get("email", "")).strip()
            orders_raw = str(row.get("orders", "0")).strip()
            status = str(row.get("status", "active")).strip() or "active"

            if not customer_id or not name or not phone_raw:
                result["skipped_invalid"] += 1
                result["errors"].append(f"Row {row_num}: Missing required fields (customer_id, name, phone)")
                continue

            valid_phone, phone_or_error = validate_phone(phone_raw)
            if not valid_phone:
                result["skipped_invalid"] += 1
                result["errors"].append(f"Row {row_num}: Invalid phone '{phone_raw}' — {phone_or_error}")
                continue

            phone = phone_or_error

            if email and not validate_email(email):
                email = ""

            try:
                orders = int(float(orders_raw)) if orders_raw else 0
            except (ValueError, TypeError):
                orders = 0

            existing_phone = Customer.query.filter_by(phone=phone).first()
            existing_id = Customer.query.filter_by(customer_id=customer_id).first()

            if existing_phone or existing_id:
                result["skipped_duplicate"] += 1
                continue

            try:
                customer = Customer(
                    customer_id=customer_id,
                    name=name,
                    email=email,
                    phone=phone,
                    orders=orders,
                    status=status if status in ["active", "inactive", "blocked"] else "active",
                )
                db.session.add(customer)
            except Exception as e:
                result["skipped_invalid"] += 1
                result["errors"].append(f"Row {row_num}: DB error — {e}")
                db.session.rollback()
                continue

            result["created"] += 1

        try:
            db.session.commit()
            result["success"] = True
        except Exception as e:
            db.session.rollback()
            result["success"] = False
            result["errors"].append(f"Database commit error: {e}")

        return result
