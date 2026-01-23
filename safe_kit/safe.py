from safe_kit.adapter import EthAdapter
from safe_kit.cache import SafeCache
from safe_kit.managers import (
    GuardManagerMixin,
    ModuleManagerMixin,
    OwnerManagerMixin,
    TokenManagerMixin,
)
from safe_kit.safe_parts import (
    SafeCacheMixin,
    SafeInfoMixin,
    SafeMessagesMixin,
    SafeTransactionsMixin,
)


class Safe(
    SafeInfoMixin,
    SafeCacheMixin,
    SafeTransactionsMixin,
    SafeMessagesMixin,
    OwnerManagerMixin,
    ModuleManagerMixin,
    TokenManagerMixin,
    GuardManagerMixin,
):
    """
    The main class for interacting with a Safe.

    This class provides a comprehensive interface for Safe operations including:
    - Basic Safe info (address, version, balance, nonce, threshold, owners)
    - Transaction creation, signing, and execution
    - Owner management (add, remove, swap owners, change threshold)
    - Module management (enable, disable, list modules)
    - Token transfers (ERC20, ERC721, native ETH)
    - Guard and fallback handler management
    """

    def __init__(
        self,
        eth_adapter: EthAdapter,
        safe_address: str,
        chain_id: int | None = None,
        enable_cache: bool = False,
        cache_ttl: int = 60,
    ):
        self.eth_adapter = eth_adapter
        self.safe_address = self.eth_adapter.to_checksum_address(safe_address)

        if not self.eth_adapter.is_contract(self.safe_address):
            raise ValueError(f"Address {self.safe_address} is not a contract")

        self.contract = self.eth_adapter.get_safe_contract(self.safe_address)
        self.chain_id = chain_id
        self.enable_cache = enable_cache
        self._cache = SafeCache(ttl=cache_ttl) if enable_cache else None

        if self.chain_id is not None:
            adapter_chain_id = self.eth_adapter.get_chain_id()
            if adapter_chain_id != self.chain_id:
                raise ValueError(
                    f"Adapter chain ID ({adapter_chain_id}) does not match "
                    f"Safe chain ID ({self.chain_id})"
                )

    @classmethod
    def create(
        cls, eth_adapter: EthAdapter, safe_address: str, chain_id: int | None = None
    ) -> "Safe":
        """
        Factory method to create a Safe instance.
        """
        return cls(eth_adapter, safe_address, chain_id)

    @classmethod
    def connect(
        cls,
        rpc_url: str,
        private_key: str,
        safe_address: str,
        chain_id: int | None = None,
    ) -> "Safe":
        """
        Convenience method to connect to a Safe with minimal configuration.

        Args:
            rpc_url: The RPC URL of the Ethereum node.
            private_key: The private key of the signer (with or without 0x prefix).
            safe_address: The address of the Safe contract.
            chain_id: Optional chain ID for validation.

        Returns:
            A Safe instance connected to the specified Safe contract.

        Example:
            safe = Safe.connect(
                rpc_url="https://mainnet.infura.io/v3/...",
                private_key="0x...",
                safe_address="0x..."
            )
        """
        from eth_account import Account
        from web3 import Web3

        from safe_kit.adapter import Web3Adapter

        w3 = Web3(Web3.HTTPProvider(rpc_url))
        signer = Account.from_key(private_key)
        adapter = Web3Adapter(web3=w3, signer=signer)
        return cls(eth_adapter=adapter, safe_address=safe_address, chain_id=chain_id)
