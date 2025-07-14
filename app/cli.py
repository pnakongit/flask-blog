import os
import click

from flask import Blueprint

bp = Blueprint("cli", __name__, cli_group=None)


@bp.cli.group()
def translate() -> None:
    """Translation and localization commands."""
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
