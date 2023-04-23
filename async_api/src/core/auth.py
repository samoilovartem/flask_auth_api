from typing import Any
from uuid import uuid4

import aiohttp
import jwt

from aiohttp import ClientConnectionError
from core.config import Config
from fastapi import Request
from jwt.exceptions import InvalidTokenError


class AuthUser:
    auth_header: str = None
    user_id: uuid4 = None
    roles: dict | list[dict[str, Any]] = dict()

    def __init__(self, auth_header):
        self.auth_header = auth_header

    async def load(self):
        headers = {'Authorization': self.auth_header}

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(Config.AUTH_API_URL, timeout=3) as resp:
                    self.roles = await resp.json()
                    return True
        except ClientConnectionError:
            try:
                jwt_payload = jwt.decode(
                    self.auth_header.split(' ')[1],
                    Config.JWT_SECRET,
                    algorithms=[Config.JWT_ALGORITHM],
                )
                user_role = jwt_payload.get('user_role')
                if user_role:
                    self.roles = [{'role_name': role} for role in user_role]
                    return True
            except InvalidTokenError:
                return False

            return False

    def is_subscriber(self):
        try:
            for role in self.roles:
                if role['role_name'] == 'subscriber' or role['role_name'] == 'superuser':
                    return True
        except TypeError:
            return False

        return False


async def get_auth_user(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    auth_user = AuthUser(auth_header)
    if not await auth_user.load():
        return None
    return auth_user
