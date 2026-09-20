import os
import uuid
from datetime import datetime
from flask import current_app


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename preserving extension."""
    ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "bin"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name


def format_phone_number(phone: str) -> str:
    """Strip spaces/dashes and ensure no leading +."""
    import re
    phone = re.sub(r"[\s\-\+\(\)]", "", str(phone))
    return phone


def render_message(template: str, customer_data: dict) -> str:
    """Replace template variables with customer data."""
    message = template
    message = message.replace("{name}", str(customer_data.get("name", "")))
    message = message.replace("{customer_id}", str(customer_data.get("customer_id", "")))
    message = message.replace("{email}", str(customer_data.get("email", "")))
    message = message.replace("{orders}", str(customer_data.get("orders", "")))
    message = message.replace("{status}", str(customer_data.get("status", "")))
    return message


def get_upload_path(subfolder: str = "") -> str:
    """Get absolute upload path."""
    base = current_app.config.get("UPLOAD_FOLDER", "static/uploads")
    if subfolder:
        return os.path.join(current_app.root_path, base, subfolder)
    return os.path.join(current_app.root_path, base)


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024**2):.1f} MB"
    return f"{size_bytes / (1024**3):.1f} GB"


def paginate_query(query, page: int, per_page: int = 25):
    """Return a Flask-SQLAlchemy pagination object."""
    return query.paginate(page=page, per_page=per_page, error_out=False)
