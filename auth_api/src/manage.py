from core.settings import settings
from gevent import monkey

monkey.patch_all()

import typer

from gevent.pywsgi import WSGIServer
from main import create_app

typer_app = typer.Typer()


@typer_app.command()
def runserver():
    app = create_app()
    http_server = WSGIServer((settings.flask_host, settings.flask_port), app)
    http_server.serve_forever()


@typer_app.command()
def create_superuser():
    pass


if __name__ == "__main__":
    typer_app()
