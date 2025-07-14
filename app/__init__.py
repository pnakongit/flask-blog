from flask import Flask

from app.db import db
from app.logging_setup import setup_logging
from app.extensions import login, mail, moment, babel, get_locale, migrate
from config import Config


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = app.config["LOGIN_VIEW"]
    login.login_message = app.config["LOGIN_MESSAGE"]

    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    setup_logging(app)

    from app.errors import bp as errors_bp
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.cli import bp as cli_bp

    app.register_blueprint(errors_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(cli_bp)

    return app


from app import models  # NOQA
