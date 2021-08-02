import threading
from abc import ABCMeta, abstractmethod
from typing import Optional

from six import add_metaclass

from freiner.storage.registry import StorageRegistry


@add_metaclass(StorageRegistry)
@add_metaclass(ABCMeta)
class Storage(object):
    """
    Base class to extend when implementing a storage backend.
    """

    def __init__(self, uri: Optional[str] = None, **kwargs):
        self.lock = threading.RLock()

    @abstractmethod
    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        increments the counter for a given rate limit key

        :param str key: the key to increment
        :param int expiry: amount in seconds for the key to expire in
        :param bool elastic_expiry: whether to keep extending the rate limit
         window every hit.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> int:
        """
        :param str key: the key to get the counter value for
        """
        raise NotImplementedError

    @abstractmethod
    def get_expiry(self, key: str) -> int:
        """
        :param str key: the key to get the expiry for
        """
        raise NotImplementedError

    @abstractmethod
    def check(self) -> bool:
        """
        check if storage is healthy
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self):
        """
        reset storage to clear limits
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self, key: str):
        """
        resets the rate limit key
        :param str key: the key to clear rate limits for
        """
        raise NotImplementedError
