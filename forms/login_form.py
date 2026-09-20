from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={"placeholder": "Enter username", "class": "form-control"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)],
        render_kw={"placeholder": "Enter password", "class": "form-control"},
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In", render_kw={"class": "btn btn-primary w-100"})
