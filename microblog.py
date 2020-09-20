from app import appl, db
from app.models import User, Post, Player, Ability


@appl.shell_context_processor
def make_shell_context():
    return {'db': db, "User": User, "Post": Post, "Player": Player, "Ability": Ability}
