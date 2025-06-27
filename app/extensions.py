from flask_login import LoginManager
from flask_mail import Mail

from app.db import db
from app.models import User

login = LoginManager()

mail = Mail()


@login.user_loader
def load_user(id_: str) -> User:
    return db.session.get(User, int(id_))
