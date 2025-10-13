import logging
import os
import time
from typing import Callable

import click

from flask import Blueprint

from app.models import Post
from app.db import db, is_db_alive
from app.search import SearchableMixin
from app.extensions import es_client

bp = Blueprint("cli", __name__, cli_group=None)


@bp.cli.group()
def translate() -> None:
    """Translation and localization commands."""
    pass


@bp.cli.group()
def es_search() -> None:
    """Elasticsearch search commands."""
    pass


@bp.cli.group()
def preprocess() -> None:
    """Preprocessing commands."""
    pass


@translate.command()
def update() -> None:
    """Update all languages."""
    if os.system("pybabel extract -F src/babel.cfg -k _l -o messages.pot .") != 0:
        raise RuntimeError("extract command failed")
    if os.system("pybabel update -i messages.pot -d src/app/translations") != 0:
        raise RuntimeError("update command failed")
    if os.path.exists("messages.pot"):
        os.remove('messages.pot')


@translate.command()
def compile() -> None:
    """Compile all languages."""
    if os.system("pybabel compile -d src/app/translations") != 0:
        raise RuntimeError("compile command failed")


@translate.command()
@click.argument('lang')
def init(lang) -> None:
    """Initialize a new language."""
    if os.system("pybabel extract -F src/babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError('extract command failed')
    if os.system(
            "pybabel init -i messages.pot -d src/app/translations -l " + lang):
        raise RuntimeError("init command failed")
    if os.path.exists("messages.pot"):
        os.remove('messages.pot')


@es_search.command()
def reindex() -> None:
    Post.reindex()


@es_search.command()
def init_indexes() -> None:
    for model in db.Model.registry.mappers:
        model_class = model.class_
        if issubclass(model_class, SearchableMixin):
            model_class.create_index()


def retry_connection(name: str, attempts: int, delay_seconds, logger_name: str, func: Callable) -> None:
    logger = logging.getLogger(logger_name)

    for attempt in range(1, attempts + 1):
        logger.info(f"Attempt {attempt}/{attempts}.")
        if func():
            logger.info(f"{name} is available")
            return
        time.sleep(delay_seconds)
        logger.info(f"{name} is not available, waiting {delay_seconds} second ...")
    raise RuntimeError(f"{name}is not available")


@preprocess.command()
@click.option("--attempts", default=10, show_default=True, help="Number of retry attempts")
@click.option("--delay_seconds", default=10, show_default=True, help="How many seconds to wait between retry attempts")
def wait_for_es(attempts: int, delay_seconds: int) -> None:
    """ Wait until Elasticsearch is ready """
    retry_connection(
        name="elasticsearch",
        attempts=attempts,
        delay_seconds=delay_seconds,
        logger_name="app.elasticsearch",
        func=es_client.is_alive
    )


@preprocess.command()
@click.option("--attempts", default=10, show_default=True, help="Number of retry attempts")
@click.option("--delay_seconds", default=10, show_default=True, help="How many seconds to wait between retry attempts")
def wait_for_db(attempts: int, delay_seconds: int) -> None:
    """ Wait until DB is ready """
    retry_connection(
        name="database",
        attempts=attempts,
        delay_seconds=delay_seconds,
        logger_name="app",
        func=is_db_alive
    )
