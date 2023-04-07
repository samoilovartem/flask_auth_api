from db.sql import db_manager
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from models.models import Role, User

user_datastore = SQLAlchemyUserDatastore(db_manager.db, User, Role)
security = Security()


def setup_user_datastore(app: Flask):
    security.init_app(app, user_datastore)
