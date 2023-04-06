from abc import ABC, abstractmethod


class SocialProvider(ABC):

    @abstractmethod
    def name(self, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def redirect_url(self, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def get_user_info(self, *args, **kwargs):
        pass
