import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "you-will-never-guess"
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///" + os.path.join(basedir, 'app.db')
    )
    SQLALCHEMY_ECHO = True
    LOGIN_VIEW = "login"
    POSTS_PER_PAGE = 3
