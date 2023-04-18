from dataclasses import dataclass
from functools import wraps
from http import HTTPStatus

import datetime
from db.redis import redis
from flask import jsonify, make_response, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request


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
            jwt_claims = get_jwt()

            user_roles = jwt_claims.get('user_role', [])

            if 'superuser' in user_roles:
                return fn(*args, **kwargs)

            if not any(role_name in user_roles for role_name in role_names):
                return (
                    jsonify({'error': 'Insufficient permissions'}),
                    HTTPStatus.FORBIDDEN,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def rate_limit(max_rate: int):
    """
    Decorator that checks that the user has not exceeded the request limit.

    Usage:
        @rate_limit(max_rate=20)
        def protected_route():
            ...

    :param max_rate: maximum number of requests per minute for the user
    :return: The decorated function if the user has not exceeded the request limit;
             otherwise, a 429 Too Many Requests error response.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if 'user_id' not in kwargs:
                return fn(*args, **kwargs)

            pipe = redis.pipeline()
            now = datetime.datetime.now()
            key = f"{kwargs['user_id']}:{now.minute}"

            pipe.incr(key, 1)
            pipe.expire(key, 59)

            result = pipe.execute()
            request_number = result[0]
            if request_number > max_rate:
                return make_response(
                    jsonify(error_code='TOO_MANY_REQUESTS',
                            message='API rate limit exceeded'),
                    HTTPStatus.TOO_MANY_REQUESTS
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator

