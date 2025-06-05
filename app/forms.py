from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=8)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=2, max=8)])
    remember_me = BooleanField("Remember Me", default=True)
    submit = SubmitField("Sign In")
