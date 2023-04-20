from uuid import uuid4

import aiohttp

from aiohttp import ClientConnectionError
from core.config import Config
from fastapi import Request


class AuthUser:
    auth_header: str = None
    user_id: uuid4 = None
    roles: dict = dict()

    def __init__(self, auth_header):
        self.auth_header = auth_header

    async def load(self):
        headers = {
            'Authorization': self.auth_header
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(Config.AUTH_API_URL,
                                       timeout=3) as resp:
                    self.roles = await resp.json()
                    return True
        except ClientConnectionError:
            return False

    def is_subscriber(self):
        for role in self.roles:
            if role['role_name'] == 'subscriber':
                return True

        return False


async def get_auth_user(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    auth_user = AuthUser(auth_header)
    if not await auth_user.load():
        return None
    return auth_user
