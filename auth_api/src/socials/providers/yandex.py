import requests
from collections import namedtuple
from functools import lru_cache
from typing import Dict
from requests.auth import HTTPBasicAuth

from core.settings import settings
from socials.interface import SocialProvider

PROVIDER_NAME = 'yandex'
AUTH_URL = 'https://oauth.yandex.ru/authorize'
TOKEN_URL = ' https://oauth.yandex.ru/token'
USERINFO_URL = 'https://login.yandex.ru/info?'
SCOPES = {
    'email': 'login:email',
    'social': 'login:info',
}

Tokens = namedtuple(
    'Tokens', ['access_token', 'expires_in', 'token_type', 'refresh_token']
)


class YandexAuthProvider(SocialProvider):
    def __init__(self):
        self.handler = settings.social_auth_handler + PROVIDER_NAME
        self.client_id = settings.yandex_auth_client_id
        self.client_secret = settings.yandex_auth_secret

    @property
    def name(self) -> str:
        return PROVIDER_NAME

    @lru_cache
    def request_url(self,
                    scopes: tuple = (SCOPES['email'], SCOPES['social'])
                    ):
        """
        Create redirect url to authorization form
        """

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
        r = requests.post(USERINFO_URL,
                          headers={"Authorization": f"OAuth {tokens.access_token}"},
                          json={"format": "js"})
        r.raise_for_status()
        return r.json()

    def __get_tokens_for_current_user(self, code: str) -> Tokens:
        """
        Retrieve access/refresh tokens for work with Google services from user
        """

        body = {
            'grant_type': 'authorization_code',
            'code': code,
        }
        r = requests.post(TOKEN_URL, data=body,
                          auth=HTTPBasicAuth(self.client_id, self.client_secret))
        print(r.content)
        r.raise_for_status()
        return Tokens(**r.json())