from typing import Any

import sqlalchemy as sa
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_babel import _, lazy_gettext as _l

from app.db import db
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l("Username "), validators=[DataRequired()])
    about_me = TextAreaField(_l("About me"), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l("Submit"))

    def __init__(self, original_username: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username: StringField) -> None:
        if username.data != self.original_username:
            stmt = sa.select(User).where(User.username == username.data)
            user = db.session.scalar(stmt)
            if user is not None:
                raise ValidationError(_("That username is taken. Please choose a different one."))


class EmptySubmitForm(FlaskForm):
    submit = SubmitField(_l("Submit"))


class PostForm(FlaskForm):
    post = TextAreaField(_l("Say something"), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l("Submit"))


class SearchForm(FlaskForm):
    q = StringField(_l("Search"), validators=[DataRequired()])

    def __init__(self, *args, **kwargs) -> None:
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "meta" not in kwargs:
            kwargs["meta"] = {"csrf": False}
        super().__init__(*args, **kwargs)
