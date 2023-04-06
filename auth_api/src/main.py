from api.common import api
from core.containers import Container
from core.settings import settings
from db.sql import create_schema_if_not_exists, db, migration
from flask_jwt_extended import JWTManager
from flask_security import Security, SQLAlchemyUserDatastore
from models.models import Role, User


def create_app():
    container = Container()
    app = container.app()
    app.container = container
    setup_app(app, settings)
    setup_database(app)
    register_blueprints(app)
    setup_security(app, settings)
    return app


def setup_app(app, app_settings):
    # app.json_encoder = ORJSONEncoder
    # app.json_decoder = ORJSONDecoder
    app.config['DEBUG'] = app_settings.flask_debug
    app.config['SECRET_KEY'] = app_settings.flask_secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = app_settings.sqlalchemy_database_uri
    app.config[
        'SQLALCHEMY_TRACK_MODIFICATIONS'
    ] = app_settings.sqlalchemy_track_modifications
    app.config['JWT_SECRET_KEY'] = app_settings.jwt_secret_key
    JWTManager(app)


def setup_database(app):
    create_schema_if_not_exists(
        app.config['SQLALCHEMY_DATABASE_URI'], settings.postgres_schema
    )
    db.init_app(app)
    migration.init_app(app, db)


def setup_security(app, app_settings):
    app.config['SECURITY_PASSWORD_SALT'] = app_settings.security_password_salt
    app.config['SECURITY_PASSWORD_HASH'] = app_settings.security_password_hash
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)


def register_blueprints(app):
    app.register_blueprint(api, url_prefix='/api')