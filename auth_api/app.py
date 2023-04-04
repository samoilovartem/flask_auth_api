from flask import Flask

from databases import db
from core.fast_json import ORJSONEncoder, ORJSONDecoder
from core.settings import settings


def create_app():
    app = Flask('auth_api')

    setup_app(app, settings)
    setup_database(app)

    return app


def setup_app(app, app_settings):
    app.json_encoder = ORJSONEncoder
    app.json_decoder = ORJSONDecoder
    app.config['DEBUG'] = app_settings.flask.debug
    app.config['SECRET_KEY'] = app_settings.flask.secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = app_settings.sqlalchemy.database_uri


def setup_database(app):
    db.init_app(app)
