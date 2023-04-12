from api.common import api
from core.containers import Container
from core.security_setup import setup_user_datastore
from core.settings import settings
from db.sql import db_manager
from flask_jwt_extended import JWTManager


def create_app():
    container = Container()
    app = container.app()
    app.container = container
    setup_app(app, settings)
    setup_database(app)
    register_blueprints(app)
    setup_security(app, settings)
    app.app_context().push()
    return app


def setup_app(app, app_settings):
    app.config['DEBUG'] = app_settings.flask_debug
    app.config['SECRET_KEY'] = app_settings.flask_secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = app_settings.sqlalchemy_database_uri
    app.config[
        'SQLALCHEMY_TRACK_MODIFICATIONS'
    ] = app_settings.sqlalchemy_track_modifications
    app.config['JWT_SECRET_KEY'] = app_settings.jwt_secret_key
    JWTManager(app)


def setup_database(app):
    db_manager.db.init_app(app)
    db_manager.migration.init_app(app, db_manager.db)


def setup_security(app, app_settings):
    app.config['SECURITY_PASSWORD_SALT'] = app_settings.security_password_salt
    app.config['SECURITY_PASSWORD_HASH'] = app_settings.security_password_hash
    setup_user_datastore(app)


def register_blueprints(app):
    app.register_blueprint(api, url_prefix='/api')


if __name__ == "__main__":
    application = create_app()
    application.run(port=8002, debug=True)
