from flask import Flask, request
from flask_migrate import Migrate

from app.db import db
from app.extensions import login, mail, moment, babel, get_locale
from app.logging_setup import setup_logging

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
migrate = Migrate(app, db)

login.init_app(app)
login.login_view = app.config["LOGIN_VIEW"]
login.login_message = app.config["LOGIN_MESSAGE"]

mail.init_app(app)

moment.init_app(app)

babel.init_app(app, locale_selector=get_locale)

setup_logging(app)

from app import routes, models, errors  # NOQA
