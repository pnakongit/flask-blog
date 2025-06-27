from typing import Any

import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
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


class EditProfileForm(FlaskForm):
    username = StringField("Username ", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username: StringField) -> None:
        if username.data != self.original_username:
            stmt = sa.select(User).where(User.username == username.data)
            user = db.session.scalar(stmt)
            if user is not None:
                raise ValidationError("That username is taken. Please choose a different one.")


class EmptySubmitForm(FlaskForm):
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    post = TextAreaField("Say something", validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField("Submit")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Request Password Reset")
