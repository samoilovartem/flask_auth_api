from collections import namedtuple
from functools import lru_cache
from typing import Dict

import requests

from core.settings import settings
from socials.interface import SocialProvider

PROVIDER_NAME = 'google'
AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
SCOPES = {
    'email': 'https://www.googleapis.com/auth/userinfo.email',
    'social': 'https://www.googleapis.com/auth/userinfo.profile',
}

Tokens = namedtuple(
    'Tokens', ['access_token', 'expires_in', 'scope', 'token_type', 'id_token']
)


class GoogleAuthProvider(SocialProvider):
    def __init__(self):
        self.handler = None
        self.client_id = settings.google_auth_client_id
        self.client_secret = settings.google_auth_secret

    @property
    def name(self) -> str:
        return PROVIDER_NAME

    @lru_cache
    def redirect_url(
        self, handler_path: str, scopes: tuple = (SCOPES['email'], SCOPES['social'])
    ):
        """
        Create redirect url to Google authorization form
        """
        self.handler = handler_path + self.name

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.handler,
            'response_type': "code",
            'scope': ' '.join(scopes),
        }
        return '{}?client_id={}&redirect_uri={}&response_type={}&scope={}'.format(
            AUTH_URL, *params.values()
        )

    def get_user_info(self, code: str) -> Dict:
        """
        Retrieve info by user
        """

        tokens = self.__get_tokens_for_current_user(code)
        params = {
            'access_token': tokens.access_token,
            'id_token': tokens.id_token,
            'token_type': tokens.token_type,
            'expires_in': tokens.expires_in,
        }
        r = requests.get(USERINFO_URL, params=params)
        r.raise_for_status()
        return r.json()

    def __get_tokens_for_current_user(self, code: str) -> Tokens:
        """
        Retrieve access/refresh tokens for work with Google services from user
        """

        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.handler,
            'grant_type': 'authorization_code',
            'code': code,
        }
        r = requests.post(TOKEN_URL, params=params)
        r.raise_for_status()
        return Tokens(**r.json())
