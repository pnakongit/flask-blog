from flask_login import LoginManager

from app.db import db
from app.models import User

login = LoginManager()


@login.user_loader
def load_user(id_: str) -> User:
    return db.session.get(User, int(id_))
