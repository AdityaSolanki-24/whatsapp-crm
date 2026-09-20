from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional


class CampaignForm(FlaskForm):
    title = StringField(
        "Campaign Title",
        validators=[DataRequired(), Length(max=200)],
        render_kw={"placeholder": "e.g. Diwali Offer 2024", "class": "form-control"},
    )
    message = TextAreaField(
        "Message",
        validators=[DataRequired()],
        render_kw={
            "placeholder": "Hi {name}, your order is ready!\nUse variables: {name}, {customer_id}, {email}, {orders}, {status}",
            "class": "form-control",
            "rows": 8,
        },
    )
    image_path = HiddenField("Image Path")
    target = SelectField(
        "Send To",
        choices=[("all", "All Customers"), ("selected", "Selected Customers")],
        default="all",
        validators=[Optional()],
        render_kw={"class": "form-select"},
    )
    submit = SubmitField("Create Campaign", render_kw={"class": "btn btn-success"})
