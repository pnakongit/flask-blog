import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from app.db import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=8)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=2, max=8)])
    remember_me = BooleanField("Remember Me", default=True)
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=8)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username: StringField) -> None:
        stmt = sa.select(User).where(User.username == username.data)
        user = db.session.scalar(stmt)

        if user is not None:
            raise ValidationError("That username is taken. Please choose a different one.")

    def validate_email(self, email: StringField) -> None:
        stmt = sa.select(User).where(User.email == email.data)
        user = db.session.scalar(stmt)

        if user is not None:
            raise ValidationError("That email is taken. Please choose a different one.")
