from threading import Thread

from flask import Flask, render_template
from flask_mail import Message

from app import app, mail
from app.models import User


def send_async_email(app: Flask, msg: Message) -> None:
    with app.app_context():
        mail.send(msg)


def send_email(
        subject: str,
        sender: str,
        recipients: list,
        text_body: str,
        html_body: str
) -> None:
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    Thread(target=send_async_email, args=(app, msg)).start()



def send_password_reset_email(user: User) -> None:
    token = user.get_reset_password_token()
    send_email("[Blog] Reset Your Password",
               sender=app.config["SENDER_EMAIL"],
               recipients=[user.email],
               text_body=render_template("emails/reset_password.txt",
                                         user=user, token=token),
               html_body=render_template("emails/reset_password.html",
                                         user=user, token=token))
