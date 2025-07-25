import cachetools
import threading
from typing import Any, Optional

class TTLCacheManager:
    """
    Thread-safe singleton cache manager using TTLCache (time-to-live).
    Ideal for temporary caching of expensive or large PDF computations.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, maxsize=1000, ttl=3600):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.cache = cachetools.TTLCache(maxsize=maxsize, ttl=ttl)
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key, None)

    def set(self, key: str, value: Any):
        self.cache[key] = value

    def clear(self):
        self.cache.clear()

    def __contains__(self, key: str):
        return key in self.cache

class LRUCacheManager:
    """
    Optional: Least Recently Used (LRU) singleton cache.
    Use for frequently accessed results that don't need to expire after time.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, maxsize=1000):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.cache = cachetools.LRUCache(maxsize=maxsize)
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key, None)

    def set(self, key: str, value: Any):
        self.cache[key] = value

    def clear(self):
        self.cache.clear()

    def __contains__(self, key: str):
        return key in self.cache

