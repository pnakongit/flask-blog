import os
import click

from flask import Blueprint

from app.models import Post
from app.extensions import db
from app.search import SearchableMixin

bp = Blueprint("cli", __name__, cli_group=None)


@bp.cli.group()
def translate() -> None:
    """Translation and localization commands."""
    pass


@bp.cli.group()
def es_search() -> None:
    """Elasticsearch search commands."""
    pass


@translate.command()
def update() -> None:
    """Update all languages."""
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot .") != 0:
        raise RuntimeError("extract command failed")
    if os.system("pybabel update -i messages.pot -d app/translations") != 0:
        raise RuntimeError("update command failed")
    if os.path.exists("messages.pot"):
        os.remove('messages.pot')


@translate.command()
def compile() -> None:
    """Compile all languages."""
    if os.system("pybabel compile -d app/translations") != 0:
        raise RuntimeError("compile command failed")


@translate.command()
@click.argument('lang')
def init(lang) -> None:
    """Initialize a new language."""
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError('extract command failed')
    if os.system(
            "pybabel init -i messages.pot -d app/translations -l " + lang):
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
