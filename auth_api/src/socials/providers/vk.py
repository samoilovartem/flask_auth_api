from collections import namedtuple
from functools import lru_cache
from typing import Dict

import requests

from core.settings import settings
from requests.auth import HTTPBasicAuth
from socials.interface import SocialProvider

PROVIDER_NAME = 'vk'
VERSION = '5.131'
AUTH_URL = 'https://oauth.vk.com/authorize'
TOKEN_URL = 'https://oauth.vk.com/access_token'
USERINFO_URL = 'https://api.vk.com/method/users.get?'
SCOPES = {
    'email': 'email',
    'social': 'friends,offline',
}

Tokens = namedtuple('Tokens', ['access_token', 'expires_in', 'user_id', 'email'])


class VkAuthProvider(SocialProvider):
    def __init__(self):
        self.handler = settings.social_auth_handler + PROVIDER_NAME
        self.client_id = settings.vk_auth_client_id
        self.client_secret = settings.vk_auth_secret

    @property
    def name(self) -> str:
        return PROVIDER_NAME

    @lru_cache
    def request_url(self, scopes: tuple = (SCOPES['email'], SCOPES['social'])):
        """
        Create redirect url to authorization form
        """

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.handler,
            'response_type': "code",
            'scope': ','.join(scopes),
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
            'user_ids': tokens.user_id,
            'fields': 'sex,bdate,city,country,photo_max_orig',
            'v': VERSION,
        }
        r = requests.post(USERINFO_URL, params=params)
        r.raise_for_status()
        response = r.json()
        if 'error' in response:
            raise ValueError(response['error']['error_msg'])
        return response['response'][0]

    def __get_tokens_for_current_user(self, code: str) -> Tokens:
        """
        Retrieve access token for work with vkontakte services from user
        """

        params = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.handler,
        }
        r = requests.post(
            TOKEN_URL,
            params=params,
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
        )
        r.raise_for_status()
        return Tokens(**r.json())
