import os

from flask import Flask

from app.db import db
from app.logging_setup import setup_logging
from app.extensions import login, mail, moment, babel, get_locale, migrate, es_client


def create_app(config_class_name=None) -> Flask:
    app = Flask(__name__)
    if config_class_name is None:
        config_class_name = os.environ.get("FLASK_CONFIG_NAME", "config.Config")
    app.config.from_object(config_class_name)

    db.init_app(app)
    migrate.init_app(app, db)

    login.init_app(app)
    login.login_view = app.config["LOGIN_VIEW"]
    login.login_message = app.config["LOGIN_MESSAGE"]

    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    setup_logging(app)
    es_client.init_app(app)

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
