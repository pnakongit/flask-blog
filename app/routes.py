from urllib.parse import urlsplit
from datetime import datetime, timezone

import sqlalchemy as sa
from flask import render_template, flash, url_for, redirect, request, g
from flask_login import current_user, login_user, logout_user, login_required
from flask.wrappers import Response
from flask_babel import _, get_locale  # NOQA
from langdetect import detect, LangDetectException

from app import app
from app.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    EmptySubmitForm,
    PostForm,
    ResetPasswordRequestForm,
    ResetPasswordForm
)
from app.db import db
from app.models import User, Post
from app.email import send_password_reset_email


@app.before_request
def add_last_seen_to_user() -> None:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.before_request
def set_locale() -> None:
    g.locale = str(get_locale())


@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
@login_required
def index() -> str | Response:
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ""

        post = Post(body=form.post.data, author=current_user, language=language)

        db.session.add(post)
        db.session.commit()
        flash(_("Your post is now live!"))
        return redirect(url_for("index"))

    page = request.args.get("page", 1, type=int)
    query = current_user.following_posts()
    posts = db.paginate(
        query,
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False
    )
    next_url = (
        url_for("index", page=posts.next_num)
        if posts.has_next else None
    )
    prev_url = (
        url_for("index", page=posts.prev_num)
        if posts.has_prev else None
    )
    return render_template(
        "index.html",
        title="Home",
        posts=posts.items,
        form=form,
        next_url=next_url,
        prev_url=prev_url
    )


@app.route('/explore')
@login_required
def explore() -> str:
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False
    )
    next_url = (
        url_for("explore", page=posts.next_num)
        if posts.has_next else None
    )
    prev_url = (
        url_for("explore", page=posts.prev_num)
        if posts.has_prev else None
    )
    return render_template(
        "index.html",
        title="Explore",
        posts=posts,
        next_url=next_url,
        prev_url=prev_url
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

            if not next_page or urlsplit(next_page).netloc != "":
                next_page = url_for("index")

            return redirect(next_page)

        flash(_("Invalid username or password"))

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

        flash(_("Congratulations, you are now a registered user!"))
        return redirect(url_for("login"))

    return render_template('register.html', title='Register', form=form)


@app.route("/users/<username>")
@login_required
def user(username: str) -> str:
    form = EmptySubmitForm()

    stmt = sa.select(User).where(User.username == username)
    user = db.first_or_404(stmt)

    page = request.args.get("page", 1, type=int)

    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False
    )
    next_url = (
        url_for("user", username=user.username, page=posts.next_num)
        if posts.has_next else None
    )
    prev_url = (
        url_for("user", username=user.username, page=posts.prev_num)
        if posts.has_prev else None
    )

    return render_template(
        "user.html",
        user=user,
        posts=posts.items,
        form=form,
        next_url=next_url,
        prev_url=prev_url
    )


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile() -> str | Response:
    form = EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("edit_profile"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template(
        "edit_profile.html",
        title="Edit Profile",
        form=form
    )


@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )
        if user:
            send_password_reset_email(user)
            flash(_("Check your email for the instructions to reset your password"))
        return redirect(url_for("login"))
    return render_template(
        "reset_password_request.html",
        title="Reset Password",
        form=form
    )


@app.route("/reset_password/<token> ", methods=["GET", "POST"])
def reset_password(token: str) -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_("Your password has been reset."))
        return redirect(url_for("login"))
    return render_template(
        "reset_password.html",
        title="Reset Password",
        form=form
    )


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username: str) -> str | Response:
    form = EmptySubmitForm()

    if form.validate_on_submit():
        stmt = sa.select(User).where(User.username == username)
        user = db.session.scalar(stmt)

        if user is None:
            flash(_("User %(username)s not found.", username=username))
            return redirect(url_for("index"))

        if user == current_user:
            flash(_("You cannot follow yourself!"))
            return redirect(url_for("user", username=username))

        current_user.follow(user)
        db.session.commit()
        flash(_("You are following %(username)s!", username=username))
        return redirect(url_for("user", username=username))

    return redirect(url_for("index"))


@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username: str) -> str | Response:
    form = EmptySubmitForm()

    if form.validate_on_submit():
        stmt = sa.select(User).where(User.username == username)
        user = db.session.scalar(stmt)

        if user is None:
            flash(_("User %(username)s not found.", username=username))
            return redirect(url_for("index"))

        if user == current_user:
            flash(_("You cannot unfollow yourself!"))
            return redirect(url_for("user", username=username))

        current_user.unfollow(user)
        db.session.commit()
        flash(_("You are not following %(username)s!", username=username))
        return redirect(url_for("user", username=username))

    return redirect(url_for("index"))
