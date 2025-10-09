import sqlalchemy as sa
import sqlalchemy.orm as so
from src.app import create_app, db
from src.app import User, Post

app = create_app()


@app.shell_context_processor
def make_shell_context() -> dict:
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}
