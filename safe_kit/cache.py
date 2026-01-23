from dataclasses import dataclass
from time import time
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """A cache entry with expiration time"""

    value: T
    expires_at: float


class SafeCache:
    """
    A simple time-based cache for Safe properties to reduce RPC calls.

    Caches Safe properties like owners, threshold, and nonce with configurable TTL.
    """

    def __init__(self, ttl: int = 60):
        """
        Initialize the cache.

        Args:
            ttl: Time to live in seconds for cached values (default: 60 seconds)
        """
        self.ttl = ttl
        self._cache: dict[str, CacheEntry[Any]] = {}

    def get(self, key: str) -> Any | None:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value or None if not found or expired
        """
        entry = self._cache.get(key)
        if entry is None:
            return None

        if time() > entry.expires_at:
            del self._cache[key]
            return None

        return entry.value

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
        """
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=time() + self.ttl,
        )

    def invalidate(self, key: str) -> None:
        """
        Invalidate a cache entry.

        Args:
            key: The cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
