import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".flaskenv"))


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///" + os.path.join(basedir, 'app.db')
    )
    LOGIN_VIEW = "auth.login"
    LOGIN_MESSAGE = "Please log in to access this page"
    POSTS_PER_PAGE = 3
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    JWT_EXPIRES_IN = 600
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    LANGUAGES = ["en", "uk"]
    MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")
    MS_TRANSLATOR_REGION = os.environ.get("MS_TRANSLATOR_REGION")
    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")


class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
    LOG_TO_STDOUT = True
    ELASTICSEARCH_URL = os.environ.get("SEARCHBOX_URL")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "testing"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
