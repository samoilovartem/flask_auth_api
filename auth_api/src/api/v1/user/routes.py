from http import HTTPStatus

from core.containers import Container
from core.utils import ServiceException, authenticate
from dependency_injector.wiring import Provide, inject
from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import get_jwt, jwt_required
from services.user import UserService

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/signup', methods=['POST'])
@inject
def signup(user_service: UserService = Provide[Container.user_service]):
    """Creates a new user
    ---
   post:
      summary: Creates a new user
      parameters:
      - in: body
        name: requestBody
        type: object
        properties:
            username:
              type: string
              example: theUser
            email:
              type: string
              example: john@email.com
            password:
              type: string
              example: '12345'
      responses:
        '200':
          description: Access/Refresh tokens Pair
          content:
            application/json:
              schema:
                type: object
                in: body
                properties:
                  access_token:
                    type: string
                    example: 'jwt_token'
                  refresh_token:
                    type: string
                    example: 'jwt_token'
      tags:
        - authorization
    """
    signup_request = user_service.validate_signup(request)
    if isinstance(signup_request, Response):
        return signup_request

    user_info = {'user-agent': request.headers.get('User-Agent')}

    try:
        access_token, refresh_token = user_service.register_user(
            signup_request.username,
            signup_request.password,
            signup_request.email,
            user_info,
        )
    except ServiceException as e:
        return make_response(jsonify(e), 400)

    return make_response(
        jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK
    )


@user.route('/login', methods=['POST'])
@inject
def login(user_service: UserService = Provide[Container.user_service]):
    """Log user in using username and password.
    ---
   post:
      summary: Log user in using username and password
      parameters:
      - in: body
        name: requestBody
        type: object
        properties:
            username:
              type: string
              example: theUser
            password:
              type: string
              example: '12345'
      responses:
        '200':
          description: Access/Refresh tokens Pair
          content:
            application/json:
              schema:
                type: object
                in: body
                properties:
                  access_token:
                    type: string
                    example: 'jwt_token'
                  refresh_token:
                    type: string
                    example: 'jwt_token'
      tags:
        - authorization
    """
    login_request = user_service.validate_login(request)
    if isinstance(login_request, Response):
        return login_request

    user_info = {'user-agent': request.headers.get('User-Agent')}

    try:
        access_token, refresh_token = user_service.login(
            login_request.username, login_request.password, user_info
        )
    except ServiceException as e:
        return make_response(jsonify(e), 400)

    return make_response(
        jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK
    )


@user.route('/refresh', methods=['PUT'])
@jwt_required(refresh=True)
@inject
def refresh(user_service: UserService = Provide[Container.user_service]):
    """
    ---
   put:
      summary: Get new access token by refresh token
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_refresh_token
        required: true
      responses:
        '200':
          description: Access/Refresh tokens Pair
          content:
            application/json:
              schema:
                type: object
                in: body
                properties:
                  access_token:
                    type: string
                    example: 'jwt_token'
                  refresh_token:
                    type: string
                    example: 'jwt_token'
      tags:
        - authorization
    """
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


@user.route('/logout', methods=['DELETE'])
@jwt_required()
@authenticate()
@inject
def logout(user_id: str, user_service: UserService = Provide[Container.user_service]):
    """
    ---
   delete:
      summary: Logout
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
        required: true
      responses:
        '200':
          description: Access/Refresh tokens Pair
          content:
            application/json:
              schema:
                type: object
                in: body
                properties:
                  access_token:
                    type: string
                    example: 'jwt_token'
                  refresh_token:
                    type: string
                    example: 'jwt_token'
      tags:
        - authorization
    """
    access_token = request.headers['Authorization'].split().pop(-1)
    refresh_token = request.json['refresh_token']

    user_service.logout(
        user_id=user_id, access_token=access_token, refresh_token=refresh_token
    )

    return make_response({}, HTTPStatus.ACCEPTED)


@user.route('/modify', methods=['PATCH'])
@jwt_required()
@authenticate()
@inject
def modify(user_id: str, user_service: UserService = Provide[Container.user_service]):
    """
    ---
   patch:
      summary: Modify user
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
        required: true
      responses:
        '200':
          description: success
      tags:
        - authorization
    """
    modify_request = user_service.validate_modify(request)
    if isinstance(modify, Response):
        return modify_request

    try:
        user_service.modify(user_id, modify_request.username, modify_request.password)
    except ServiceException as err:
        return make_response(jsonify(err), 400)

    return make_response({'msg': 'Password has been updated'}, HTTPStatus.ACCEPTED)


@user.route('/auth_history', methods=["GET"])
@jwt_required()
@authenticate()
@inject
def auth_history(
    user_id: str, user_service: UserService = Provide[Container.user_service]
):
    """
    ---
   get:
      summary: Get User history
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
        required: true
      responses:
        '200':
          description: success
          content:
            application/json:
              schema:
                type: array
                items:
                    type: object
                    properties:
                      uuid:
                        type: string
                      time:
                        type: string
                      fingerprint:
                        type: string
      tags:
        - authorization
    """
    try:
        history = user_service.get_auth_history(user_id)
    except ServiceException as err:
        return make_response(jsonify(err), 400)

    return make_response(jsonify(history), HTTPStatus.OK)
