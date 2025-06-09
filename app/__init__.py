from flask import Flask
from flask_migrate import Migrate

from app.db import db

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
migrate = Migrate(app, db)

from app import routes, models  # NOQA
