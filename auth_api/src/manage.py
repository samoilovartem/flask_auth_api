from gevent import monkey

monkey.patch_all()

import click

from core.security_setup import user_datastore
from core.settings import settings
from db.sql import db_manager
from flask.cli import with_appcontext
from gevent.pywsgi import WSGIServer
from main import create_app
from models.models import Role, RoleType
from sqlalchemy.exc import IntegrityError

app = create_app()


@click.group()
def cli():
    pass


@cli.command()
def runserver():
    http_server = WSGIServer((settings.flask_host, settings.flask_port), app)
    http_server.serve_forever()


@click.command()
@click.option('--login', default='admin', help='Superuser login')
@click.option('--password', default='admin', help='Superuser password')
@with_appcontext
def create_superuser(login: str, password: str) -> None:
    try:
        with db_manager.transaction():
            user = user_datastore.create_user(login=login, password=password)
            superuser_role = Role(name=RoleType.superuser, description='Superuser role')
            user_datastore.add_role_to_user(user, superuser_role)
    except IntegrityError:
        raise ValueError(
            f'Failed to create superuser! User with login {login} already exists.',
        )


cli.add_command(create_superuser)

if __name__ == "__main__":
    cli()
