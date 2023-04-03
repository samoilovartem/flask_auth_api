import abc
import json
from typing import Any, Optional

from configs import loguru_config
from loguru import logger

logger.add(**loguru_config)


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        pass


class JsonFileStorage(BaseStorage):
    """
    A class that provides methods for saving and retrieving data in a JSON file format.
    """

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        try:
            with open(self.file_path, 'w') as f:
                json.dump(state, f)
        except FileNotFoundError as e:
            logger.error('The file {} has not been found. Error: {}', self.file_path, e)

    def retrieve_state(self) -> dict:
        state = {}
        try:
            with open(self.file_path, 'r') as f:
                state = json.load(f)
        except FileNotFoundError as e:
            logger.error('The file {} has not been found. Error: {}', self.file_path, e)
        return state


class State:
    """
    A class that manages application state by delegating data persistence to a storage object.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = {}

    def set_state(self, key: str, value: Any) -> None:
        if self.state is not None:
            self.state[key] = value
            self.storage.save_state(self.state)

    def get_state(self, key: str) -> Any:
        self.state = self.storage.retrieve_state()
        return self.state.get(key)
