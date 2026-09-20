import os
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required
from models.instagram import InstagramAccount, InstagramContent, InstagramLead, InstagramNotification, InstagramMedia, InstagramWebhookEvent, InstagramAutomationRule, InstagramSettings, InstagramConversation
from database.db import db
from forms.instagram_forms import InstagramContentForm, InstagramAutomationRuleForm, InstagramSettingsForm
from services.content_generator_service import ContentGeneratorService
from services.lead_service import LeadService
from services.analytics_service import AnalyticsService
from services.notification_service import NotificationService
from services.instagram_service import InstagramService
from services.instagram_token_service import InstagramTokenService
from werkzeug.utils import secure_filename

instagram_bp = Blueprint("instagram", __name__, url_prefix="/instagram")
lead_service = LeadService()
analytics_service = AnalyticsService()

@instagram_bp.route("/")
@login_required
def dashboard():
    """Main Instagram Manager Dashboard"""
    accounts_count = InstagramAccount.query.count()
    posts_count = InstagramContent.query.filter_by(content_type="post").count()
    reels_count = InstagramContent.query.filter_by(content_type="reel").count()
    leads_count = InstagramLead.query.count()
    
    recent_activities = InstagramContent.query.order_by(InstagramContent.created_at.desc()).limit(5).all()
    
    return render_template(
        "instagram/dashboard.html",
        stats={
            "accounts": accounts_count,
            "posts": posts_count,
            "reels": reels_count,
            "leads": leads_count
        },
        activities=recent_activities
    )

@instagram_bp.route("/accounts")
@login_required
def accounts():
    """Manage connected Instagram Accounts"""
    accounts = InstagramAccount.query.all()
    return render_template("instagram/accounts.html", accounts=accounts)

@instagram_bp.route("/accounts/<int:account_id>/disconnect", methods=["POST"])
@login_required
def disconnect_account(account_id):
    """Disconnect an active Instagram account"""
    account = InstagramAccount.query.get_or_404(account_id)
    account.status = "disconnected"
    db.session.commit()
    NotificationService.create("Account Disconnected", f"Instagram account {account.username} was disconnected.", "account_disconnected")
    flash(f"Account {account.username} disconnected successfully.", "info")
    return redirect(url_for("instagram.accounts"))

@instagram_bp.route("/accounts/<int:account_id>/refresh", methods=["POST"])
@login_required
def refresh_token(account_id):
    """Manually force an Access Token refresh"""
    token_service = InstagramTokenService()
    res = token_service.refresh_token(account_id)
    if res["success"]:
        flash("Token refreshed successfully.", "success")
    else:
        flash(f"Failed to refresh token: {res.get('error')}", "danger")
    return redirect(url_for("instagram.accounts"))

@instagram_bp.route("/setup-wizard")
@login_required
def setup_wizard():
    """Onboarding wizard for Facebook Developer & Instagram connection"""
    step = request.args.get("step", 1, type=int)
    return render_template(f"instagram/wizard/step_{step}.html", current_step=step)

@instagram_bp.route("/content")
@login_required
def content_manager():
    """Manage Posts, Reels, and Stories"""
    content_type = request.args.get("type", "post")
    page = request.args.get("page", 1, type=int)
    contents = InstagramContent.query.filter_by(content_type=content_type).order_by(InstagramContent.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template("instagram/content_list.html", contents=contents, type=content_type)

@instagram_bp.route("/content/create", methods=["GET", "POST"])
@login_required
def content_create():
    """Create or Schedule a new Post, Reel, or Story"""
    form = InstagramContentForm()
    
    # Populate accounts
    accounts = InstagramAccount.query.filter_by(status="active").all()
    form.account_id.choices = [(a.id, a.username) for a in accounts]
    
    if not accounts:
        flash("Please connect an Instagram account first.", "warning")
        return redirect(url_for("instagram.accounts"))

    if form.validate_on_submit():
        from flask import current_app
        from utils.helpers import generate_unique_filename
        
        media_path = None
        if form.media_file.data:
            f = form.media_file.data
            filename = secure_filename(f.filename)
            unique_name = generate_unique_filename(filename)
            
            # Save to specific folder based on content_type (post/reel/story)
            ctype = form.content_type.data.lower()
            folder_path = os.path.join(current_app.root_path, "static", "uploads", "instagram", f"{ctype}s")
            os.makedirs(folder_path, exist_ok=True)
            
            full_path = os.path.join(folder_path, unique_name)
            f.save(full_path)
            media_path = f"static/uploads/instagram/{ctype}s/{unique_name}"

        content = InstagramContent(
            account_id=form.account_id.data,
            content_type=form.content_type.data.lower(),
            title=form.title.data,
            caption=form.caption.data,
            hashtags=form.hashtags.data,
            media_paths=media_path,
            status=form.status.data,
            schedule_time=form.schedule_time.data
        )
        db.session.add(content)
        db.session.commit()
        
        flash(f"{form.content_type.data.capitalize()} '{content.title}' saved successfully.", "success")
        return redirect(url_for("instagram.content_manager", type=content.content_type))

    return render_template("instagram/content_form.html", form=form)

@instagram_bp.route("/ai-studio", methods=["GET"])
@login_required
def ai_studio():
    """Render Local AI Content Studio Interface"""
    return render_template("instagram/ai_studio.html")

@instagram_bp.route("/api/ai-generate", methods=["POST"])
@login_required
def ai_generate_api():
    """AJAX endpoint for the AI Content Studio Generator"""
    data = request.json
    topic = data.get("topic", "")
    gen_type = data.get("type", "captions") # captions, hashtags, ctas, ideas, calendar
    
    generator = ContentGeneratorService()
    
    if gen_type == "captions":
        result = generator.generate_captions(topic)
    elif gen_type == "hashtags":
        result = generator.generate_hashtags(topic)
    elif gen_type == "ctas":
        result = generator.generate_ctas()
    elif gen_type == "descriptions":
        result = generator.generate_descriptions(topic)
    elif gen_type == "story_ideas":
        result = generator.generate_story_ideas(topic)
    elif gen_type == "reel_ideas":
        result = generator.generate_reel_ideas(topic)
    elif gen_type == "calendar":
        result = generator.generate_calendar(topic)
    else:
        return jsonify({"success": False, "error": "Invalid generation type"}), 400
        
    return jsonify({"success": True, "data": result})

@instagram_bp.route("/media-library")
@login_required
def media_library():
    """Instagram specific media library"""
    page = request.args.get("page", 1, type=int)
    media = InstagramMedia.query.order_by(InstagramMedia.created_at.desc()).paginate(page=page, per_page=24, error_out=False)
    return render_template("instagram/media_library.html", media=media)

@instagram_bp.route("/calendar")
@login_required
def content_calendar():
    """Visual Drag and Drop Calendar for content"""
    scheduled_contents = InstagramContent.query.filter(InstagramContent.schedule_time != None).all()
    return render_template("instagram/calendar.html", events=scheduled_contents)

@instagram_bp.route("/leads")
@login_required
def leads():
    """Lead Pipeline and Management"""
    page = request.args.get("page", 1, type=int)
    leads_data = lead_service.get_all_leads(page=page)
    return render_template("instagram/leads.html", leads=leads_data)

@instagram_bp.route("/leads/<int:lead_id>/convert", methods=["POST"])
@login_required
def convert_lead(lead_id):
    """Convert an IG lead into a CRM Customer"""
    phone = request.form.get("phone")
    email = request.form.get("email", "")
    if not phone:
        flash("Phone number is required to create a CRM Customer.", "danger")
        return redirect(url_for('instagram.leads'))
        
    result = lead_service.convert_to_customer(lead_id, phone, email)
    if result["success"]:
        flash("Lead converted to CRM Customer successfully!", "success")
    else:
        flash(result["error"], "danger")
    return redirect(url_for('instagram.leads'))

@instagram_bp.route("/notifications")
@login_required
def notifications():
    """Central Notification Center"""
    notifs = InstagramNotification.query.order_by(InstagramNotification.created_at.desc()).all()
    return render_template("instagram/notifications.html", notifications=notifs)

@instagram_bp.route("/notifications/mark_all", methods=["POST"])
@login_required
def mark_all_read():
    """Mark all notifications as read"""
    InstagramNotification.query.filter_by(is_read=False).update({"is_read": True})
    db.session.commit()
    return redirect(url_for('instagram.notifications'))

@instagram_bp.route("/inbox")
@login_required
def inbox():
    """DM Conversations Interface"""
    conversations = InstagramConversation.query.order_by(InstagramConversation.last_message_at.desc()).all()
    return render_template("instagram/inbox.html", conversations=conversations)

@instagram_bp.route("/analytics")
@login_required
def analytics():
    """Instagram Analytics Dashboard"""
    stats = analytics_service.get_dashboard_stats()
    return render_template("instagram/analytics.html", stats=stats)
    
@instagram_bp.route("/automation", methods=["GET"])
@login_required
def automation():
    """Manage Automation Rules"""
    rules = InstagramAutomationRule.query.all()
    return render_template("instagram/automation.html", rules=rules)

@instagram_bp.route("/automation/create", methods=["GET", "POST"])
@login_required
def automation_create():
    """Create a new Automation Rule"""
    form = InstagramAutomationRuleForm()
    accounts = InstagramAccount.query.filter_by(status="active").all()
    form.account_id.choices = [(a.id, a.username) for a in accounts]
    
    contents = InstagramContent.query.order_by(InstagramContent.created_at.desc()).all()
    form.target_content_id.choices = [(0, "All Content")] + [(c.id, f"{c.content_type.upper()}: {c.title or c.id}") for c in contents]

    if form.validate_on_submit():
        rule = InstagramAutomationRule(
            name=form.name.data,
            account_id=form.account_id.data,
            rule_type=form.rule_type.data,
            match_type=form.match_type.data,
            target_content_id=form.target_content_id.data if form.target_content_id.data != 0 else None,
            trigger_keywords=form.trigger_keywords.data,
            reply_template=form.reply_template.data,
            is_active=form.is_active.data
        )
        db.session.add(rule)
        db.session.commit()
        flash("Automation Rule Created", "success")
        return redirect(url_for('instagram.automation'))
    
    return render_template("instagram/automation_form.html", form=form)

@instagram_bp.route("/automation/<int:rule_id>/toggle", methods=["POST"])
@login_required
def automation_toggle(rule_id):
    """Enable or disable a specific automation rule"""
    rule = InstagramAutomationRule.query.get_or_404(rule_id)
    rule.is_active = not rule.is_active
    db.session.commit()
    flash(f"Rule {'Enabled' if rule.is_active else 'Disabled'} successfully.", "success")
    return redirect(url_for('instagram.automation'))

@instagram_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Admin Settings for the Instagram Manager"""
    settings_obj = InstagramSettings.query.first()
    if not settings_obj:
        settings_obj = InstagramSettings()
        db.session.add(settings_obj)
        db.session.commit()
        
    form = InstagramSettingsForm(obj=settings_obj)
    if form.validate_on_submit():
        settings_obj.automation_enabled = form.automation_enabled.data
        settings_obj.default_lead_status = form.default_lead_status.data
        settings_obj.notify_on_lead = form.notify_on_lead.data
        settings_obj.notify_on_dm = form.notify_on_dm.data
        db.session.commit()
        flash("Settings saved successfully.", "success")
        return redirect(url_for('instagram.settings'))
        
    return render_template("instagram/settings.html", form=form)

@instagram_bp.route("/api-tester")
@login_required
def api_tester():
    """Admin API Testing Panel"""
    accounts = InstagramAccount.query.filter_by(status="active").all()
    return render_template("instagram/api_tester.html", accounts=accounts)

@instagram_bp.route("/oauth/login")
@login_required
def oauth_login():
    """Redirect to Facebook OAuth Login"""
    redirect_uri = url_for("instagram.oauth_callback", _external=True)
    url = InstagramService().get_authorization_url(redirect_uri)
    return redirect(url)

@instagram_bp.route("/oauth/callback")
@login_required
def oauth_callback():
    """Process Facebook OAuth callback and connect accounts"""
    code = request.args.get("code")
    if not code:
        flash("Authorization failed or cancelled.", "danger")
        return redirect(url_for("instagram.setup_wizard"))
        
    redirect_uri = url_for("instagram.oauth_callback", _external=True)
    ig_service = InstagramService()
    
    token_data = ig_service.exchange_code_for_token(code, redirect_uri)
    if "access_token" not in token_data:
        flash(f"Token exchange error: {token_data}", "danger")
        return redirect(url_for("instagram.setup_wizard"))
        
    long_token_data = ig_service.get_long_lived_token(token_data["access_token"])
    
    connected_accounts = ig_service.connect_instagram_accounts(long_token_data)
    if connected_accounts:
        flash(f"Successfully connected {len(connected_accounts)} Instagram account(s).", "success")
    else:
        flash("No Instagram Business accounts found on your connected Facebook Pages.", "warning")
        
    return redirect(url_for("instagram.accounts"))

@instagram_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    """Facebook Webhook for Instagram Messaging and Comments"""
    if request.method == "GET":
        verify_token = current_app.config.get("FB_WEBHOOK_VERIFY_TOKEN")
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == verify_token:
            return challenge, 200
        return "Forbidden", 403
        
    if request.method == "POST":
        data = request.json
        if data and data.get("object") == "instagram":
            # Determine webhook event type
            event_type = "unknown"
            try:
                event_type = data["entry"][0]["changes"][0]["field"]
            except (IndexError, KeyError):
                pass
                
            # Log webhook payload to database
            event = InstagramWebhookEvent(event_type=event_type, payload=json.dumps(data))
            db.session.add(event)
            db.session.commit()
            
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "comments":
                        # Forward to the automation service for auto-reply / lead generation
                        pass
        return "OK", 200