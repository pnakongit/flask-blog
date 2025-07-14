from flask import render_template
from werkzeug.exceptions import NotFound, InternalServerError

from app.db import db
from app.errors import bp


@bp.app_errorhandler(NotFound)
def page_not_found(error: NotFound) -> (str, int):
    return render_template("errors/not_found.html"), NotFound.code


@bp.app_errorhandler(InternalServerError)
def internal_server_error(error: InternalServerError) -> (str, int):
    db.session.rollback()
    return render_template("errors/internal_server_error.html"), InternalServerError.code

