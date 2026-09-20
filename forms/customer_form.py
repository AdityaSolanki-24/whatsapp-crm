from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange


class CustomerForm(FlaskForm):
    customer_id = StringField(
        "Customer ID",
        validators=[DataRequired(), Length(max=100)],
        render_kw={"placeholder": "e.g. CUST001", "class": "form-control"},
    )
    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(max=200)],
        render_kw={"placeholder": "Customer full name", "class": "form-control"},
    )
    email = StringField(
        "Email",
        validators=[Optional(), Email(), Length(max=200)],
        render_kw={"placeholder": "customer@email.com", "class": "form-control"},
    )
    phone = StringField(
        "Phone (with country code)",
        validators=[DataRequired(), Length(max=30)],
        render_kw={"placeholder": "e.g. 919876543210", "class": "form-control"},
    )
    orders = IntegerField(
        "Total Orders",
        validators=[Optional(), NumberRange(min=0)],
        default=0,
        render_kw={"class": "form-control"},
    )
    status = SelectField(
        "Status",
        choices=[("active", "Active"), ("inactive", "Inactive"), ("blocked", "Blocked")],
        render_kw={"class": "form-select"},
    )
    submit = SubmitField("Save Customer", render_kw={"class": "btn btn-success"})
