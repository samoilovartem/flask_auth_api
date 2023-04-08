from gevent import monkey

monkey.patch_all()

import click

from core.security_setup import user_datastore
from core.settings import settings
from db.sql import db_manager
from flask.cli import with_appcontext
from gevent.pywsgi import WSGIServer
from main import create_app
from models.models import ROLE_DESCRIPTIONS, Role, RoleType
from sqlalchemy.exc import IntegrityError

app = create_app()


@click.group()
def cli():
    pass


@cli.command()
def runserver():
    http_server = WSGIServer((settings.flask_host, settings.flask_port), app)
    http_server.serve_forever()
    print(f'Running on {settings.flask_host}:{settings.flask_port}...')


@cli.command()
def create_roles():
    with app.app_context():
        for role_type in RoleType:
            role = Role(name=role_type, description=ROLE_DESCRIPTIONS[role_type])
            db_manager.db.session.add(role)
        db_manager.db.session.commit()
    click.echo(message='All roles created successfully!', color=True)


@cli.command()
@click.option('--username', default='admin', help='Superuser username')
@click.option('--password', default='admin', help='Superuser password')
@with_appcontext
def create_superuser(username: str, password: str) -> None:
    try:
        with db_manager.transaction():
            user = user_datastore.create_user(username=username, password=password)
            user_datastore.add_role_to_user(user, RoleType.superuser)
            click.echo(
                message=f'Superuser {username} created successfully!', color=True
            )
    except IntegrityError:
        # raise ValueError(
        #     f'Failed to create superuser! User with username "{username}" already exists.',
        # )
        click.echo(
            message=f'Failed to create superuser! User with username "{username}" already exists.',
            color=True,
        )


cli.add_command(create_superuser)
cli.add_command(create_roles)

if __name__ == "__main__":
    cli()
