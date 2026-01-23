from __future__ import annotations

from typing import Any

from safe_kit.adapter import EthAdapter
from safe_kit.cache import SafeCache


class SafeContext:
    eth_adapter: EthAdapter
    safe_address: str
    contract: Any
    chain_id: int | None
    enable_cache: bool
    _cache: SafeCache | None

    def get_nonce(self) -> int:  # pragma: no cover
        raise NotImplementedError

    def get_threshold(self) -> int:  # pragma: no cover
        raise NotImplementedError
