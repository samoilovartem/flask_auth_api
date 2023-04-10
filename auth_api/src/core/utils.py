from dataclasses import dataclass
from functools import wraps
from http import HTTPStatus

from db.redis import redis
from flask import jsonify, make_response, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from models.models import User


@dataclass
class ServiceException(Exception):
    error_code: str
    message: str


def authenticate():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            access_token = request.headers['Authorization'].split().pop(-1)

            if not redis.get(access_token) == b'':
                return make_response(
                    jsonify(
                        error_code='ACCESS_TOKEN_EXPIRED',
                        message='Access token has expired',
                    ),
                    HTTPStatus.UNAUTHORIZED,
                )

            jwt = get_jwt()
            if 'user_id' not in jwt:
                return make_response(
                    jsonify(
                        error_mode='IDENTITY_MISSING',
                        message='User id not found in decrypted content',
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            kwargs['user_id'] = jwt['user_id']
            return fn(*args, **kwargs)  # pragma: no cover

        return decorator

    return wrapper


def get_auth_headers(token: str):
    return {'Authorization': 'Bearer ' + token}


def jwt_roles_required(*role_names):
    """
    Decorator for requiring one or more roles to access a route. Users with the 'superuser' role
    will always have access to the route, regardless of the specified roles.

    Usage:
        @jwt_roles_required('role1', 'role2')
        def protected_route():
            ...

    :param role_names: One or more role names (strings) required for accessing the route.
    :return: The decorated function if the user has the required roles or the 'superuser' role;
             otherwise, a 403 Forbidden response with an "Insufficient permissions" error message.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            user = User.query.get(user_id)
            if user is None:
                return jsonify({"error": "User not found"}), HTTPStatus.NOT_FOUND

            if user.has_role('superuser'):
                return fn(*args, **kwargs)

            if not any(user.has_role(role_name) for role_name in role_names):
                return (
                    jsonify({"error": "Insufficient permissions"}),
                    HTTPStatus.FORBIDDEN,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator
