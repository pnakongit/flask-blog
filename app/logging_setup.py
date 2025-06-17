import os
import logging
import time

from logging.handlers import RotatingFileHandler

from flask import Flask


def setup_logging(app: Flask) -> None:
    if not app.debug:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler("logs/blog.log", maxBytes=10240,
                                           backupCount=10)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )

        formatter.converter = time.gmtime

        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Blog startup')
