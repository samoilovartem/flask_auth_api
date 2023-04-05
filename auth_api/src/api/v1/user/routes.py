from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import get_jwt, jwt_required

from src.core.containers import Container
from src.core.utils import ServiceException, authenticate
from src.services.user import UserService

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/signup', methods=["POST"])
@inject
def signup(user_service: UserService = Provide[Container.user_service]):
    """Creates a new user"""
    signup_request = user_service.validate_signup(request)
    if isinstance(signup_request, Response):
        return signup_request

    user_info = {'user-agent': request.headers.get('User-Agent')}

    access_token, refresh_token = user_service.register_user(
        signup_request.username,
        signup_request.password,
        signup_request.email,
        user_info,
    )

    return make_response(
        jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK
    )


@user.route('/auth', methods=["POST"])
@inject
def login(user_service: UserService = Provide[Container.user_service]):
    """Log user in using username and password."""
    login_request = user_service.validate_login(request)
    if isinstance(login_request, Response):
        return login_request

    user_info = {'user-agent': request.headers.get('User-Agent')}

    access_token, refresh_token = user_service.login(
        login_request.username, login_request.password, user_info
    )

    return make_response(
        jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK
    )


@user.route('/auth', methods=["PUT"])
@jwt_required(refresh=True)
@inject
def refresh(user_service: UserService = Provide[Container.user_service]):
    jwt = get_jwt()
    refresh_token = request.headers['Authorization'].split().pop(-1)

    if 'user_id' not in jwt:
        return make_response(
            jsonify(
                error_mode='IDENTITY_MISSING',
                message="User id not found in decrypted content",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    access_token, refresh_token = user_service.refresh(
        user_id=jwt['user_id'], refresh_token=refresh_token
    )

    return make_response(
        jsonify(access_token=access_token, refresh_token=refresh_token)
    )


@user.route('/auth/logout', methods=["POST"])
@jwt_required()
@authenticate()
@inject
def logout(user_id: str, user_service: UserService = Provide[Container.user_service]):
    access_token = request.headers['Authorization'].split().pop(-1)
    request_json = request.json
    refresh_token = request_json['refresh_token']

    access_token, refresh_token = user_service.logout(
        user_id=user_id, access_token=access_token, refresh_token=refresh_token
    )

    return make_response(
        jsonify(access_token=access_token, refresh_token=refresh_token)
    )


@user.route('/auth', methods=["PATCH"])
@jwt_required()
@authenticate()
@inject
def modify(user_id: str, user_service: UserService = Provide[Container.user_service]):
    modify_request = user_service.validate_modify(request)
    if isinstance(modify, Response):
        return modify_request

    try:
        user_service.modify(user_id, modify_request.username, modify_request.password)
    except ServiceException as err:
        return make_response(jsonify(err), 400)

    return make_response({}, HTTPStatus.ACCEPTED)


@user.route('/auth', methods=["GET"])
@jwt_required()
@authenticate()
@inject
def auth_history(
    user_id: str, user_service: UserService = Provide[Container.user_service]
):
    try:
        history = user_service.get_auth_history(user_id)
    except ServiceException as err:
        return make_response(jsonify(err), 400)

    return make_response(jsonify(history), HTTPStatus.OK)
