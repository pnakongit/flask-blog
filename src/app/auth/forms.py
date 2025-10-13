import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_babel import _, lazy_gettext as _l

from app.db import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired(), Length(min=2, max=8)])
    password = PasswordField(_l("Password"), validators=[DataRequired(), Length(min=2, max=8)])
    remember_me = BooleanField(_l("Remember Me"), default=True)
    submit = SubmitField(_l("Sign In"))


class RegistrationForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired(), Length(min=2, max=8)])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(_l("Repeat Password"), validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(_l("Register"))

    def validate_username(self, username: StringField) -> None:
        stmt = sa.select(User).where(User.username == username.data)
        user = db.session.scalar(stmt)

        if user is not None:
            raise ValidationError(_("That username is taken. Please choose a different one."))

    def validate_email(self, email: StringField) -> None:
        stmt = sa.select(User).where(User.email == email.data)
        user = db.session.scalar(stmt)

        if user is not None:
            raise ValidationError(_("That email is taken. Please choose a different one."))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset"))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(
        _l("Repeat Password"),
        validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField(_l("Request Password Reset"))
