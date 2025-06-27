from flask import Flask
from flask_migrate import Migrate

from app.db import db
from app.extensions import login, mail
from app.logging_setup import setup_logging

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
migrate = Migrate(app, db)

login.init_app(app)
login.login_view = app.config["LOGIN_VIEW"]

mail.init_app(app)

setup_logging(app)

from app import routes, models, errors  # NOQA
