from dataclasses import dataclass
from functools import wraps
from http import HTTPStatus

from db.redis import redis
from flask import jsonify, make_response, request
from flask_jwt_extended import get_jwt


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
                    jsonify(error_code='ACCESS_TOKEN_EXPIRED',
                            message='Access token has expired'),
                    HTTPStatus.UNAUTHORIZED
                )

            jwt = get_jwt()
            if 'user_id' not in jwt:
                return make_response(
                    jsonify(error_mode='IDENTITY_MISSING',
                            message='User id not found in decrypted content'),
                    HTTPStatus.BAD_REQUEST)

            kwargs['user_id'] = jwt['user_id']
            return fn(*args, **kwargs)  # pragma: no cover

        return decorator

    return wrapper


def get_auth_headers(token: str):
    return {'Authorization': 'Bearer ' + token}
