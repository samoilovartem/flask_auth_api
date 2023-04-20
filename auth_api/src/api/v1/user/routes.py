from http import HTTPStatus

from core.containers import Container
from core.settings import settings
from core.utils import ServiceException, authenticate, rate_limit
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
      requestBody:
        content:
          application/json:
            schema:
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
        return make_response(jsonify(e), HTTPStatus.BAD_REQUEST)

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
      requestBody:
        content:
          application/json:
            schema:
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
        return make_response(jsonify(e), HTTPStatus.BAD_REQUEST)

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
      security:
        - bearerAuth: []
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
@rate_limit(settings.user_rate_limit)
@inject
def logout(user_id: str, user_service: UserService = Provide[Container.user_service]):
    """
    ---
   delete:
      summary: Logout
      security:
        - bearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
                type: object
                properties:
                    refresh_token:
                      type: string
                      example: jwt_refresh_token
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
@rate_limit(settings.user_rate_limit)
@inject
def modify(user_id: str, user_service: UserService = Provide[Container.user_service]):
    """
    ---
   patch:
      summary: Modify user
      security:
        - bearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
                oneOf:
                    - type: object
                      properties:
                        username:
                          type: string
                          example: new_name_user
                          required: true
                        password:
                          type: string
                          example: 123458
                          required: true
                    - type: object
                      properties:
                        username:
                          type: string
                          example: new_name_user
                          required: true
                    - type: object
                      properties:
                        password:
                          type: string
                          example: new_name_user
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
        return make_response(jsonify(err), HTTPStatus.BAD_REQUEST)

    return make_response({'msg': 'Password has been updated'}, HTTPStatus.ACCEPTED)


@user.route('/auth_history', methods=["GET"])
@jwt_required()
@authenticate()
@rate_limit(settings.user_rate_limit)
@inject
def auth_history(
        user_id: str, user_service: UserService = Provide[Container.user_service]
):
    """
    ---
   get:
      summary: Get User history
      security:
        - bearerAuth: []
      parameters:
        - in: query
          name: page
          type: string
          example: 1
          description: Pagination page
        - in: query
          name: per_page
          type: int
          example: 3
          description: events per page
      responses:
        '200':
          description: success
          content:
            application/json:
              schema:
                type: object
                properties:
                    next_page:
                        type: integer
                    prev_page:
                        type: integer
                    pages:
                        type: integer
                    per_page:
                        type: integer
                    total:
                        type: integer
                    events:
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
        '404':
            description: Page not found
      tags:
        - authorization
    """
    try:
        kwargs = {key: int(request.args[key]) for key in request.args}
        history = user_service.get_auth_history(user_id, **kwargs)
    except ServiceException as err:
        return make_response(jsonify(err), HTTPStatus.BAD_REQUEST)
    return make_response(jsonify(history), HTTPStatus.OK)


@user.route('/<uuid:some_user_id>/roles', methods=['GET'])
@jwt_required()
@inject
def get_user_roles_list(
        some_user_id: str,
        user_service: UserService = Provide[Container.user_service]):
    roles_list = user_service.get_user_roles_list(some_user_id)
    result = [{'role_id': role.id,
               'role_name': role.name} for role in roles_list]
    return jsonify(result)


@user.route('/roles', methods=['GET'])
@jwt_required()
@authenticate()
@inject
def get_current_user_roles_list(
        user_id: str,
        user_service: UserService = Provide[Container.user_service]):
    roles_list = user_service.get_user_roles_list(user_id)
    result = [{'role_id': role.id,
               'role_name': role.name} for role in roles_list]
    return jsonify(result)
