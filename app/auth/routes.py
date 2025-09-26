from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import render_template, flash, url_for, redirect, request
from flask_login import login_user, logout_user, current_user
from flask.wrappers import Response
from flask_babel import _

from app.auth import bp
from app.models import db, User

from app.auth.emails import send_password_reset_email
from app.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm
)


@bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        stmt = sa.select(User).where(User.username == form.username.data)
        user = db.session.scalar(stmt)

        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")

            if not next_page or urlsplit(next_page).netloc != "":
                next_page = url_for("main.index")

            return redirect(next_page)

        flash(_("Invalid username or password"))

    return render_template(
        "auth/login.html",
        title="Sign In",
        form=form
    )


@bp.route("/logout")
def logout() -> Response:
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash(_("Congratulations, you are now a registered user!"))
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title="Register", form=form)


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )
        if user:
            send_password_reset_email(user)
            flash(_("Check your email for the instructions to reset your password"))
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password_request.html",
        title="Reset Password",
        form=form
    )


@bp.route("/reset_password/<token> ", methods=["GET", "POST"])
def reset_password(token: str) -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_("Your password has been reset."))
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password.html",
        title="Reset Password",
        form=form
    )
