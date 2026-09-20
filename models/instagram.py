from datetime import datetime
from database.db import db

class InstagramAccount(db.Model):
    __tablename__ = "instagram_accounts"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    account_name = db.Column(db.String(100))
    ig_user_id = db.Column(db.String(100), unique=True, nullable=False)
    profile_picture_url = db.Column(db.String(500))
    access_token = db.Column(db.Text, nullable=False)
    token_expiry = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="active")  # active, disconnected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    contents = db.relationship("InstagramContent", backref="account", lazy=True, cascade="all, delete-orphan")
    rules = db.relationship("InstagramAutomationRule", backref="account", lazy=True, cascade="all, delete-orphan")
    leads = db.relationship("InstagramLead", backref="account", lazy=True, cascade="all, delete-orphan")


class InstagramContent(db.Model):
    __tablename__ = "instagram_contents"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("instagram_accounts.id"), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)  # post, reel, story
    title = db.Column(db.String(200))
    caption = db.Column(db.Text)
    hashtags = db.Column(db.Text)
    media_paths = db.Column(db.Text)  # Comma-separated paths or JSON
    status = db.Column(db.String(20), default="draft")  # draft, scheduled, published, failed
    schedule_time = db.Column(db.DateTime, nullable=True)
    ig_media_id = db.Column(db.String(100), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)


class InstagramAutomationRule(db.Model):
    __tablename__ = "instagram_automation_rules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="Untitled Rule")
    account_id = db.Column(db.Integer, db.ForeignKey("instagram_accounts.id"), nullable=False)
    rule_type = db.Column(db.String(20), nullable=False)  # comment_reply, dm_reply, lead_capture
    target_content_id = db.Column(db.Integer, db.ForeignKey("instagram_contents.id"), nullable=True) # Null = all
    match_type = db.Column(db.String(20), default="contains") # exact, contains
    trigger_keywords = db.Column(db.String(255), nullable=False) # comma-separated
    reply_template = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InstagramLead(db.Model):
    __tablename__ = "instagram_leads"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("instagram_accounts.id"), nullable=False, index=True)
    crm_customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    username = db.Column(db.String(100), nullable=False)
    profile_url = db.Column(db.String(255))
    source_content_id = db.Column(db.Integer, db.ForeignKey("instagram_contents.id"), nullable=True)
    matched_keyword = db.Column(db.String(50))
    initial_comment = db.Column(db.Text)
    pipeline_status = db.Column(db.String(50), default="New Lead", index=True) # New Lead, Interested, Follow Up, Qualified, Customer
    notes = db.Column(db.Text)
    tags = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InstagramAutomationLog(db.Model):
    __tablename__ = "instagram_automation_logs"

    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey("instagram_automation_rules.id"), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey("instagram_accounts.id"), nullable=False)
    event_type = db.Column(db.String(50))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InstagramConversation(db.Model):
    __tablename__ = "instagram_conversations"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("instagram_accounts.id"), nullable=False)
    ig_thread_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    last_message = db.Column(db.Text)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)


class InstagramNotification(db.Model):
    __tablename__ = "instagram_notifications"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    event_type = db.Column(db.String(50)) # post_published, lead_created, token_expiry
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InstagramMedia(db.Model):
    __tablename__ = "instagram_media"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("instagram_accounts.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    media_type = db.Column(db.String(50)) # image, video
    folder = db.Column(db.String(50)) # posts, reels, stories, templates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InstagramSchedule(db.Model):
    __tablename__ = "instagram_schedules"

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("instagram_contents.id"), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending") # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InstagramAnalytics(db.Model):
    __tablename__ = "instagram_analytics"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("instagram_accounts.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    followers_count = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    profile_views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InstagramWebhookEvent(db.Model):
    __tablename__ = "instagram_webhook_events"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("instagram_accounts.id"), nullable=True)
    event_type = db.Column(db.String(50)) # comments, mentions, messages, unknown
    payload = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InstagramSettings(db.Model):
    __tablename__ = "instagram_settings"

    id = db.Column(db.Integer, primary_key=True)
    automation_enabled = db.Column(db.Boolean, default=True)
    default_lead_status = db.Column(db.String(50), default="New Lead")
    notify_on_lead = db.Column(db.Boolean, default=True)
    notify_on_dm = db.Column(db.Boolean, default=True)
    notify_on_comment = db.Column(db.Boolean, default=False)
    content_defaults = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)