from __future__ import annotations

from typing import cast

from safe_kit.contract_types import SafeIsOwnerParams

from .base import SafeContext


class SafeInfoMixin(SafeContext):
    def get_address(self) -> str:
        """Returns the address of the Safe."""
        return self.safe_address

    def get_chain_id(self) -> int:
        """Returns the chain ID of the connected network."""
        if self.chain_id is not None:
            return self.chain_id
        return self.eth_adapter.get_chain_id()

    def get_version(self) -> str:
        """Returns the version of the Safe contract."""
        return cast(str, self.contract.functions.VERSION().call())

    def get_balance(self) -> int:
        """Returns the ETH balance of the Safe."""
        return self.eth_adapter.get_balance(self.safe_address)

    def is_owner(self, address: str) -> bool:
        """Checks if an address is an owner of the Safe."""
        params: SafeIsOwnerParams = {"owner": address}
        return cast(bool, self.contract.functions.isOwner(**params).call())
