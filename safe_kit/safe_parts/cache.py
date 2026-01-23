from __future__ import annotations

from typing import cast

from .base import SafeContext


class SafeCacheMixin(SafeContext):
    def get_nonce(self) -> int:
        """Returns the current nonce of the Safe."""
        if self._cache is not None:
            cached: int | None = self._cache.get("nonce")
            if cached is not None:
                return cached

        nonce = cast(int, self.contract.functions.nonce().call())

        if self._cache is not None:
            self._cache.set("nonce", nonce)

        return nonce

    def get_threshold(self) -> int:
        """Returns the threshold of the Safe."""
        if self._cache is not None:
            cached: int | None = self._cache.get("threshold")
            if cached is not None:
                return cached

        threshold = cast(int, self.contract.functions.getThreshold().call())

        if self._cache is not None:
            self._cache.set("threshold", threshold)

        return threshold

    def get_owners(self) -> list[str]:
        """Returns the owners of the Safe."""
        if self._cache is not None:
            cached: list[str] | None = self._cache.get("owners")
            if cached is not None:
                return cached

        owners = cast(list[str], self.contract.functions.getOwners().call())

        if self._cache is not None:
            self._cache.set("owners", owners)

        return owners

    def clear_cache(self) -> None:
        """Clears the Safe info cache."""
        if self._cache is not None:
            self._cache.clear()

    def invalidate_cache(self, key: str) -> None:
        """Invalidates a specific cache entry."""
        if self._cache is not None:
            self._cache.invalidate(key)
