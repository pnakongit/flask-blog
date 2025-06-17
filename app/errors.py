from flask import render_template
from werkzeug.exceptions import NotFound, InternalServerError

from app.db import db
from app import app


@app.errorhandler(NotFound)
def page_not_found(error: NotFound) -> (str, int):
    return render_template("errors/not_found.html"), NotFound.code


@app.errorhandler(InternalServerError)
def internal_server_error(error: InternalServerError) -> (str, int):
    db.session.rollback()
    return render_template("errors/internal_server_error.html"), InternalServerError.code
