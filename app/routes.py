from flask import render_template, flash, url_for, redirect
from flask.wrappers import Response

from app import app
from app.forms import LoginForm


@app.route("/")
@app.route("/index")
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
    form = LoginForm()

    if form.validate_on_submit():
        flash(f"Login requested for user {form.username.data}, "
              f"remember_me={form.remember_me.data}!", "success"
              )
        return redirect(url_for("index"))

    return render_template(
        "login.html",
        title='Sign In',
        form=form
    )
