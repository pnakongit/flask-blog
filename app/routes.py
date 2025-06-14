from urllib.parse import urlsplit
from datetime import datetime, timezone

from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user, login_user, logout_user, login_required
from flask.wrappers import Response
import sqlalchemy as sa

from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.db import db
from app.models import User


@app.before_request
def add_last_seen_to_user() -> None:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/")
@app.route("/index")
@login_required
def index() -> str:
    user = {"username": "Pablo"}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template(
        "index.html",
        title="Home",
        user=user,
        posts=posts
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        stmt = sa.select(User).where(User.username == form.username.data)
        user = db.session.scalar(stmt)

        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            print("Next page: ",next_page)

            if not next_page or urlsplit(next_page).netloc != "":
                next_page = url_for("index")

            return redirect(next_page)

        flash("Invalid username or password")

    return render_template(
        "login.html",
        title='Sign In',
        form=form
    )


@app.route("/logout")
def logout() -> Response:
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))

    return render_template('register.html', title='Register', form=form)


@app.route("/users/<username>")
@login_required
def user(username: str) -> str:
    stmt = sa.select(User).where(User.username == username)
    user = db.first_or_404(stmt)

    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'},
    ]

    return render_template("user.html", user=user, posts=posts)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile() -> str | Response:
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template(
        "edit_profile.html",
        title="Edit Profile",
        form=form
    )
