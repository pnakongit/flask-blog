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
    LOGIN_MESSAGE = "Please log in to access this page"
    POSTS_PER_PAGE = 3
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    JWT_EXPIRES_IN = 600
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    LANGUAGES = ["en", "uk"]
    MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")
    MS_TRANSLATOR_REGION = os.environ.get("MS_TRANSLATOR_REGION")
