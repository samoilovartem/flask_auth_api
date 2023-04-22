from typing import Iterable

from core.utils import ServiceException
from socials.interface import SocialProvider
from socials.providers.google import GoogleAuthProvider
from socials.providers.vk import VkAuthProvider
from socials.providers.yandex import YandexAuthProvider

providers = [GoogleAuthProvider, YandexAuthProvider, VkAuthProvider]

class SocialAuthService:
    def __init__(self):
        self.providers = dict()
        self.__init_providers__()

    def __init_providers__(self):
        for _ in providers:
            provider: SocialProvider = _()
            provider_name: str = provider.name
            self.providers[provider_name.lower()] = provider

    def get_provider_by_name(self, name: str) -> SocialProvider:
        if name.lower() in self.providers:
            return self.providers[name]
        raise ServiceException(
            message='Social Provider not found', error_code='NOT FOUND'
        )

    def iter(self) -> Iterable[SocialProvider]:
        for _ in self.providers:
            yield self.providers[_]


social_auth_service = SocialAuthService()