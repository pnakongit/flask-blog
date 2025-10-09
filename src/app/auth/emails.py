from flask import render_template, current_app

from src.app.models import User
from src.app.email import send_email


def send_password_reset_email(user: User) -> None:
    token = user.get_reset_password_token()
    send_email("[Blog] Reset Your Password",
               sender=current_app.config["SENDER_EMAIL"],
               recipients=[user.email],
               text_body=render_template("emails/../templates/emails/reset_password.txt",
                                         user=user, token=token),
               html_body=render_template("emails/../templates/emails/reset_password.html",
                                         user=user, token=token))
