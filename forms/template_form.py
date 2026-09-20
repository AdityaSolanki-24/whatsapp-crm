from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class TemplateForm(FlaskForm):
    template_name = StringField(
        "Template Name",
        validators=[DataRequired(), Length(max=200)],
        render_kw={"placeholder": "e.g. Welcome Message", "class": "form-control"},
    )
    category = SelectField(
        "Category",
        choices=[
            ("welcome", "Welcome"),
            ("offer", "Offer"),
            ("festival", "Festival"),
            ("order_update", "Order Update"),
            ("custom", "Custom"),
        ],
        render_kw={"class": "form-select"},
    )
    template_content = TextAreaField(
        "Template Content",
        validators=[DataRequired()],
        render_kw={
            "placeholder": "Hi {name}, welcome to our store!\nAvailable variables: {name}, {customer_id}, {email}, {orders}, {status}",
            "class": "form-control",
            "rows": 10,
        },
    )
    submit = SubmitField("Save Template", render_kw={"class": "btn btn-success"})
