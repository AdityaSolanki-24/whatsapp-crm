from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from forms.login_form import LoginForm
from services.auth_service import AuthService
from services.audit_service import SystemService
from app import limiter

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        admin = auth_service.authenticate(form.username.data, form.password.data)
        if admin:
            login_user(admin, remember=form.remember_me.data)
            SystemService.log_audit("Admin Login", f"Successful login for {admin.username}")
            next_page = request.args.get("next")
            flash("Welcome back!", "success")
            return redirect(next_page or url_for("dashboard.index"))
        else:
            flash("Invalid username or password.", "danger")
            SystemService.log_audit("Failed Login Attempt", f"Attempted username: {form.username.data}")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    SystemService.log_audit("Admin Logout", f"Logout for {current_user.username}")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
