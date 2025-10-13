from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import OperationalError


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def is_db_alive() -> bool:
    try:
        db.session.execute(text("SELECT 1"))
        return True
    except OperationalError as e:
        return False
