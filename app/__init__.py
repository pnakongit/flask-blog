from flask import Flask
from flask_migrate import Migrate

from app.db import db
from app.extensions import login

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
migrate = Migrate(app, db)

login.init_app(app)
login.login_view = app.config["LOGIN_VIEW"]

from app import routes, models  # NOQA
