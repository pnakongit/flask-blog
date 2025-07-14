from flask import current_app, request
from flask_babel import Babel
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_migrate import Migrate

from app.db import db
from app.models import User

login = LoginManager()
mail = Mail()
moment = Moment()
babel = Babel()
migrate = Migrate()

@login.user_loader
def load_user(id_: str) -> User:
    return db.session.get(User, int(id_))


def get_locale() -> str:
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])
    # return "uk"
