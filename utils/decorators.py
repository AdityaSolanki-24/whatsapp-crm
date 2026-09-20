from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def login_required_admin(f):
    """Ensure only logged-in admin can access the route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function
