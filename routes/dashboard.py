from flask import Blueprint, render_template
from flask_login import login_required
from services.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)
dashboard_service = DashboardService()


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    stats = dashboard_service.get_stats()
    return render_template("dashboard/dashboard.html", **stats)
