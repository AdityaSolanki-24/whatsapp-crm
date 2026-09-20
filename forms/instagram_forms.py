from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional, Length
from utils.constants import IG_CONTENT_TYPES, IG_CONTENT_STATUS, ALLOWED_IMAGE_EXTENSIONS

# Expand allowed extensions for Instagram to include video formats
IG_ALLOWED_MEDIA = ALLOWED_IMAGE_EXTENSIONS.union({"mp4", "mov"})

class InstagramContentForm(FlaskForm):
    content_type = SelectField("Content Type", choices=[(c, c.capitalize()) for c in IG_CONTENT_TYPES], validators=[DataRequired()])
    account_id = SelectField("Instagram Account", coerce=int, validators=[DataRequired()])
    
    title = StringField("Internal Title", validators=[DataRequired(), Length(max=200)])
    caption = TextAreaField("Caption", validators=[Optional()])
    hashtags = TextAreaField("Hashtags", validators=[Optional()])
    
    media_file = FileField("Upload Media", validators=[Optional(), FileAllowed(IG_ALLOWED_MEDIA, "Images and videos only!")])
    status = SelectField("Status", choices=[(k, v) for k, v in IG_CONTENT_STATUS.items()], default="draft")
    schedule_time = DateTimeField("Schedule Time", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    submit = SubmitField("Save Content")


class InstagramAutomationRuleForm(FlaskForm):
    name = StringField("Rule Name", validators=[DataRequired(), Length(max=100)])
    account_id = SelectField("Instagram Account", coerce=int, validators=[DataRequired()])
    rule_type = SelectField("Rule Type", choices=[
        ("comment_reply", "Comment Automation"),
        ("dm_reply", "DM Automation"),
        ("lead_capture", "Lead Capture Automation")
    ], validators=[DataRequired()])
    match_type = SelectField("Keyword Match Type", choices=[
        ("exact", "Exact Match"),
        ("contains", "Contains Match")
    ], default="contains")
    target_content_id = SelectField("Target Assigned Content (Optional)", coerce=int, validators=[Optional()])
    trigger_keywords = StringField("Keywords (comma separated)", validators=[DataRequired()])
    reply_template = TextAreaField("Reply Message(s) - separate multiples with '|'", validators=[DataRequired()])
    is_active = BooleanField("Enable Rule", default=True)
    submit = SubmitField("Save Rule")


class InstagramSettingsForm(FlaskForm):
    automation_enabled = BooleanField("Enable Global Automation", default=True)
    default_lead_status = StringField("Default Lead Status", default="New Lead")
    notify_on_lead = BooleanField("Notify on New Lead Capture", default=True)
    notify_on_dm = BooleanField("Notify on New Direct Message", default=True)
    submit = SubmitField("Save Settings")