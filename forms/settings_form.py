from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class SettingsForm(FlaskForm):
    whatsapp_phone_id = StringField(
        "WhatsApp Phone Number ID",
        validators=[DataRequired(), Length(max=200)],
        render_kw={"placeholder": "e.g. 123456789012345", "class": "form-control"},
    )
    whatsapp_access_token = TextAreaField(
        "WhatsApp Access Token",
        validators=[DataRequired()],
        render_kw={
            "placeholder": "Paste your WhatsApp Business API access token here",
            "class": "form-control",
            "rows": 4,
        },
    )
    submit = SubmitField("Save Settings", render_kw={"class": "btn btn-success"})
