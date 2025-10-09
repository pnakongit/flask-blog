import os
import logging
import time

from logging.handlers import RotatingFileHandler

from flask import Flask


def setup_logging(app: Flask) -> None:
    if not app.debug and not app.testing:
        app.logger.setLevel(logging.INFO)

        if app.config.get("LOG_TO_STDOUT"):
            app_handler = logging.StreamHandler()
        else:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            app_handler = RotatingFileHandler("logs/blog.log", maxBytes=10240,
                                               backupCount=10)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )

        formatter.converter = time.gmtime
        app_handler.setFormatter(formatter)
        app_handler.setLevel(logging.INFO)

        app.logger.addHandler(app_handler)

        # Setup logger for elasticsearch
        es_logger = logging.getLogger("app.elasticsearch")
        es_logger.setLevel(logging.INFO)
        es_logger.propagate = False

        es_handler = logging.StreamHandler()
        es_formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] - %(message)s")
        es_formatter.converter = time.gmtime
        es_handler.setFormatter(es_formatter)
        es_handler.setLevel(logging.INFO)
        es_logger.addHandler(es_handler)

        app.logger.info('Blog startup')
