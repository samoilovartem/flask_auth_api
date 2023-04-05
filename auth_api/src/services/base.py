from collections import namedtuple
from http import HTTPStatus
from typing import Type, Union

from flask import Request, Response, make_response
from pydantic import BaseModel, ValidationError

Rcode = namedtuple('Rcode', 'code message')


class BaseService:
    USER_NOT_FOUND = Rcode('USER_NOT_FOUND', 'Unknown user UUID')
    LOGIN_EXISTS = Rcode('LOGIN_EXISTS', 'This username is already taken')
    INVALID_REFRESH_TOKEN = Rcode('INVALID_REFRESH_TOKEN',
                                  'This refresh token is invalid')
    WRONG_PASSWORD = Rcode('WRONG_PASSWORD', 'The password is incorrect')
    EMAIL_EXISTS = Rcode('EMAIL_EXISTS', 'This email address is already used')
    ACCESS_TOKEN_EXPIRED = Rcode('ACCESS_TOKEN_EXPIRED',
                                 'Access token has expired')

    def __init__(self):
        pass

    def _validate(
            self, request: Request, model: Type[BaseModel]
    ) -> Union[BaseModel, Response]:
        request_json = request.json
        try:
            create_request = model(**request_json)
        except ValidationError as err:
            # TO DO: logging
            return make_response({
                'message': "Bad request!",
                'status': 400,
                'Error': str(err),
            },
                HTTPStatus.BAD_REQUEST
            )
        return create_request
