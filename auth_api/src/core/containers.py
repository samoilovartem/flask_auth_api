from dependency_injector import containers, providers
from dependency_injector.ext import flask
from flask import Flask
from services.user import UserService


class Container(containers.DeclarativeContainer):
    app = flask.Application(Flask, __name__)

    wiring_config = containers.WiringConfiguration(
        packages=[
            'api.v1.routes',
            'api.v1.user.routes',
        ],
    )

    user_service = providers.Factory(UserService)
