from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, jsonify, current_app
)
from flask_login import login_required
from forms.campaign_form import CampaignForm
from services.campaign_service import CampaignService
from services.customer_service import CustomerService
from models.campaign import Campaign
from models.campaign_log import CampaignLog
from models.customer import Customer
from models.message_template import MessageTemplate

campaigns_bp = Blueprint("campaigns", __name__, url_prefix="/campaigns")
campaign_service = CampaignService()
customer_service = CustomerService()


@campaigns_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("campaigns/campaigns.html", campaigns=campaigns)


@campaigns_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CampaignForm()
    customers = customer_service.get_active_customers()
    templates = MessageTemplate.query.all()

    if form.validate_on_submit():
        try:
            campaign = campaign_service.create_campaign(
                title=form.title.data,
                message=form.message.data,
                image_path=form.image_path.data or None,
            )
            flash(f"Campaign '{campaign.title}' created.", "success")
            return redirect(url_for("campaigns.view", campaign_id=campaign.id))
        except Exception as e:
            current_app.logger.exception(e)
            flash(str(e), "danger")
    elif request.method == "POST":
        for field, errors in form.errors.items():
            for error in errors:
                field_label = getattr(form, field).label.text if hasattr(getattr(form, field), 'label') else field
                flash(f"Validation error in {field_label}: {error}", "danger")

    return render_template(
        "campaigns/campaign_form.html",
        form=form,
        customers=customers,
        templates=templates,
        action="Create",
    )


@campaigns_bp.route("/<int:campaign_id>")
@login_required
def view(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    customers = customer_service.get_active_customers()
    logs = CampaignLog.query.filter_by(campaign_id=campaign_id).order_by(
        CampaignLog.sent_at.desc()
    ).limit(100).all()
    return render_template(
        "campaigns/campaign_view.html",
        campaign=campaign,
        customers=customers,
        logs=logs,
    )


@campaigns_bp.route("/<int:campaign_id>/send", methods=["POST"])
@login_required
def send(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.status == "running":
        flash("Campaign is already running.", "warning")
        return redirect(url_for("campaigns.view", campaign_id=campaign_id))

    target = request.form.get("target", "all")
    customer_ids = None

    if target == "selected":
        ids_raw = request.form.getlist("customer_ids")
        if not ids_raw:
            flash("No customers selected.", "warning")
            return redirect(url_for("campaigns.view", campaign_id=campaign_id))
        customer_ids = [int(i) for i in ids_raw if i.isdigit()]

    base_url = request.host_url.rstrip("/")
    result = campaign_service.send_campaign(
        campaign_id=campaign_id,
        customer_ids=customer_ids,
        base_url=base_url,
    )

    if result["success"]:
        flash(
            f"Campaign sent! ✅ {result['sent']} sent, ❌ {result['failed']} failed out of {result['total']}.",
            "success" if result["failed"] == 0 else "warning",
        )
    else:
        flash(f"Campaign failed: {result.get('error', 'Unknown error')}", "danger")

    return redirect(url_for("campaigns.view", campaign_id=campaign_id))


@campaigns_bp.route("/<int:campaign_id>/history")
@login_required
def history(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "")

    logs_query = CampaignLog.query.filter_by(campaign_id=campaign_id)
    if status_filter in ("sent", "failed", "pending"):
        logs_query = logs_query.filter_by(status=status_filter)

    logs = logs_query.order_by(CampaignLog.sent_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template(
        "campaigns/campaign_history.html",
        campaign=campaign,
        logs=logs,
        status_filter=status_filter,
    )


@campaigns_bp.route("/<int:campaign_id>/delete", methods=["POST"])
@login_required
def delete(campaign_id):
    deleted = campaign_service.delete_campaign(campaign_id)
    if deleted:
        flash("Campaign deleted.", "success")
    else:
        flash("Campaign not found.", "warning")
    return redirect(url_for("campaigns.index"))
