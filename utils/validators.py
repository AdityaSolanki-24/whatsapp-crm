import re
import os
from utils.constants import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_CSV_EXTENSIONS


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate phone number - must be digits only, 10-15 chars."""
    phone_clean = re.sub(r"[\s\-\+\(\)]", "", str(phone))
    if not phone_clean.isdigit():
        return False, "Phone must contain only digits (with optional country code)"
    if len(phone_clean) < 10 or len(phone_clean) > 15:
        return False, "Phone must be 10-15 digits"
    return True, phone_clean


def validate_email(email: str) -> bool:
    """Basic email validation."""
    if not email:
        return True
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def allowed_image_file(filename: str) -> bool:
    """Check if file extension is allowed for images."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def allowed_csv_file(filename: str) -> bool:
    """Check if file extension is allowed for CSV."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_CSV_EXTENSIONS
    )


def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename."""
    filename = os.path.basename(filename)
    filename = re.sub(r"[^\w\.\-]", "_", filename)
    return filename


def validate_message_length(message: str) -> tuple[bool, str]:
    """Validate WhatsApp message length."""
    if not message or not message.strip():
        return False, "Message cannot be empty"
    if len(message) > 4096:
        return False, "Message exceeds WhatsApp limit of 4096 characters"
    return True, ""
