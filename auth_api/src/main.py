from api.common import api
from core import documentation
from core.containers import Container
from core.security_setup import setup_user_datastore
from core.settings import settings
from db.sql import db_manager
from flask_jwt_extended import JWTManager
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from flask_cors import CORS


def create_app():
    container = Container()
    app = container.app()
    app.container = container
    setup_app(app, settings)
    setup_database(app)
    register_blueprints(app)
    setup_security(app, settings)
    setup_documentation(app)
    # Add CORS politics
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.app_context().push()
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
    db_manager.create_schema_if_not_exists(
        app.config['SQLALCHEMY_DATABASE_URI'], settings.postgres_schema
    )
    db_manager.db.init_app(app)
    db_manager.migration.init_app(app, db_manager.db)


def setup_security(app, app_settings):
    app.config['SECURITY_PASSWORD_SALT'] = app_settings.security_password_salt
    app.config['SECURITY_PASSWORD_HASH'] = app_settings.security_password_hash
    setup_user_datastore(app)


def register_blueprints(app):
    app.register_blueprint(api, url_prefix='/api')


def setup_documentation(app):
    spec = APISpec(
        title="Auth API",
        version="1.0.0",
        openapi_version="3.0.2",
        info=dict(description="Sprint 1"),
        plugins=[FlaskPlugin()],
        servers=[{
          "url": "http://localhost:5000",
          "description": "Development server"}
        ]
    )
    documentation.load_spec(app, spec)
    with open(settings.documentation_path, 'w', encoding='utf-8') as f:
        f.write(spec.to_yaml())


if __name__ == "__main__":
    application = create_app()
    application.run(port=8002, debug=True)
