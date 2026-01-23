from typing import TYPE_CHECKING, Any, cast

from hexbytes import HexBytes

from safe_kit.adapter import EthAdapter
from safe_kit.cache import SafeCache
from safe_kit.contract_types import (
    SafeApproveHashParams,
    SafeExecTransactionParams,
    SafeGetTransactionHashParams,
    SafeIsOwnerParams,
    SafeRequiredTxGasParams,
)
from safe_kit.errors import handle_contract_error
from safe_kit.managers import (
    GuardManagerMixin,
    ModuleManagerMixin,
    OwnerManagerMixin,
    TokenManagerMixin,
)
from safe_kit.types import SafeTransaction, SafeTransactionData

if TYPE_CHECKING:
    from safe_kit.builder import TransactionBuilder

EIP1271_MAGIC_VALUE = "0x1626ba7e"


class Safe(
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

    def get_address(self) -> str:
        """
        Returns the address of the Safe.
        """
        return self.safe_address

    def get_chain_id(self) -> int:
        """
        Returns the chain ID of the connected network.
        """
        if self.chain_id is not None:
            return self.chain_id
        return self.eth_adapter.get_chain_id()

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

    def get_version(self) -> str:
        """
        Returns the version of the Safe contract.
        """
        return cast(str, self.contract.functions.VERSION().call())

    def get_balance(self) -> int:
        """
        Returns the ETH balance of the Safe.
        """
        return self.eth_adapter.get_balance(self.safe_address)

    def get_nonce(self) -> int:
        """
        Returns the current nonce of the Safe.
        """
        if self._cache:
            cached: int | None = self._cache.get("nonce")
            if cached is not None:
                return cached

        nonce = cast(int, self.contract.functions.nonce().call())

        if self._cache:
            self._cache.set("nonce", nonce)

        return nonce

    def get_threshold(self) -> int:
        """
        Returns the threshold of the Safe.
        """
        if self._cache:
            cached: int | None = self._cache.get("threshold")
            if cached is not None:
                return cached

        threshold = cast(int, self.contract.functions.getThreshold().call())

        if self._cache:
            self._cache.set("threshold", threshold)

        return threshold

    def get_owners(self) -> list[str]:
        """
        Returns the owners of the Safe.
        """
        if self._cache:
            cached: list[str] | None = self._cache.get("owners")
            if cached is not None:
                return cached

        owners = cast(list[str], self.contract.functions.getOwners().call())

        if self._cache:
            self._cache.set("owners", owners)

        return owners

    def is_owner(self, address: str) -> bool:
        """
        Checks if an address is an owner of the Safe.
        """
        params: SafeIsOwnerParams = {"owner": address}
        return cast(bool, self.contract.functions.isOwner(**params).call())

    def create_transaction(
        self, transaction_data: SafeTransactionData
    ) -> SafeTransaction:
        """
        Creates a Safe transaction ready to be signed.
        """
        if transaction_data.nonce is None:
            transaction_data.nonce = self.get_nonce()

        return SafeTransaction(data=transaction_data)

    def tx(self) -> "TransactionBuilder":
        """
        Creates a new TransactionBuilder for fluent transaction creation.

        Returns:
            A TransactionBuilder instance

        Example:
            tx = safe.tx() \\
                .send_eth("0x123...", 1000000000000000000) \\
                .send_erc20("0xToken...", "0x456...", 100) \\
                .build()
        """
        from safe_kit.builder import TransactionBuilder

        return TransactionBuilder(self)

    def create_batch_transaction(
        self,
        transactions: list[SafeTransactionData],
        multisend_address: str = "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
    ) -> SafeTransaction:
        """
        Creates a batched Safe transaction using MultiSend.

        This is a convenience method that automatically encodes multiple transactions
        into a single MultiSend call, eliminating the need to manually import and use
        the MultiSend class.

        Args:
            transactions: A list of SafeTransactionData objects to batch together
            multisend_address: The address of the MultiSend contract
                (default: canonical MultiSend v1.3.0 address)

        Returns:
            A SafeTransaction containing the batched transactions

        Example:
            tx1 = SafeTransactionData(to="0x123...", value=1000000, data="0x")
            tx2 = SafeTransactionData(to="0x456...", value=2000000, data="0x")
            batch_tx = safe.create_batch_transaction([tx1, tx2])
        """
        from safe_kit.multisend import MultiSend

        encoded_data = MultiSend.encode_transactions(transactions)
        multisend_data = "0x8d80ff0a" + encoded_data.hex()

        batch_tx_data = SafeTransactionData(
            to=multisend_address,
            value=0,
            data=multisend_data,
            operation=1,  # DelegateCall
        )

        return self.create_transaction(batch_tx_data)

    def sign_transaction(
        self, safe_transaction: SafeTransaction, method: str = "eth_sign_typed_data"
    ) -> SafeTransaction:
        """
        Signs a Safe transaction with the current signer.
        Supported methods: "eth_sign_typed_data" (EIP-712), "eth_sign" (legacy).
        """
        signer_address = self.eth_adapter.get_signer_address()
        if not signer_address:
            raise ValueError("No signer configured in the adapter")

        chain_id = self.eth_adapter.get_chain_id()

        if method == "eth_sign_typed_data":
            eip712_data = safe_transaction.data.get_eip712_data(
                chain_id, self.safe_address
            )
            signature = self.eth_adapter.sign_typed_data(eip712_data)
        elif method == "eth_sign":
            tx_hash = self.get_transaction_hash(safe_transaction)
            signature = self.eth_adapter.sign_message(tx_hash)
            # Adjust v for eth_sign: v += 4
            # Signature is r(32) + s(32) + v(1)
            # We need to parse it, adjust v, and reconstruct
            sig_bytes = HexBytes(signature)
            r = sig_bytes[:32]
            s = sig_bytes[32:64]
            v = sig_bytes[64]
            v += 4
            signature = (r + s + bytes([v])).hex()
        else:
            raise ValueError(f"Unsupported signing method: {method}")

        safe_transaction.add_signature(signer_address, signature)
        return safe_transaction

    def add_signature(
        self, safe_transaction: SafeTransaction, owner_address: str, signature: str
    ) -> SafeTransaction:
        """
        Adds a signature to a Safe transaction.
        """
        owner_address = self.eth_adapter.to_checksum_address(owner_address)
        safe_transaction.add_signature(owner_address, signature)
        return safe_transaction

    def add_prevalidated_signature(
        self, safe_transaction: SafeTransaction, owner_address: str
    ) -> SafeTransaction:
        """
        Adds a pre-validated signature for a given owner.
        v=1, r=owner, s=0.
        """
        owner_address = self.eth_adapter.to_checksum_address(owner_address)
        # Signature: r(32) + s(32) + v(1)
        # r = owner address, padded to 32 bytes
        # s = 0, padded to 32 bytes
        # v = 1
        r = owner_address.lower().replace("0x", "").zfill(64)
        s = "0" * 64
        v = "01"
        signature = "0x" + r + s + v
        safe_transaction.add_signature(owner_address, signature)
        return safe_transaction

    def get_transaction_hash(self, safe_transaction: SafeTransaction) -> str:
        """
        Returns the hash of the Safe transaction.
        """
        params: SafeGetTransactionHashParams = {
            "to": safe_transaction.data.to,
            "value": safe_transaction.data.value,
            "data": HexBytes(safe_transaction.data.data),
            "operation": safe_transaction.data.operation,
            "safeTxGas": safe_transaction.data.safe_tx_gas,
            "baseGas": safe_transaction.data.base_gas,
            "gasPrice": safe_transaction.data.gas_price,
            "gasToken": safe_transaction.data.gas_token,
            "refundReceiver": safe_transaction.data.refund_receiver,
            "_nonce": (
                safe_transaction.data.nonce
                if safe_transaction.data.nonce is not None
                else 0
            ),
        }

        return cast(
            str,
            self.contract.functions.getTransactionHash(**params).call().hex(),
        )

    def approve_hash(self, hash_to_approve: str) -> str:
        """
        Approves a hash on-chain.
        """
        try:
            params: SafeApproveHashParams = {"hashToApprove": HexBytes(hash_to_approve)}
            tx_hash = self.contract.functions.approveHash(**params).transact(
                {"from": self.eth_adapter.get_signer_address()}
            )
            return cast(str, tx_hash.hex())
        except Exception as e:
            raise handle_contract_error(e) from e

    def execute_transaction(
        self,
        safe_transaction: SafeTransaction,
        wait_for_receipt: bool = False,
        gas: int | None = None,
    ) -> str:
        """
        Executes a Safe transaction.
        """
        # Sort signatures
        sorted_signatures = safe_transaction.sorted_signatures_bytes

        try:
            params: SafeExecTransactionParams = {
                "to": safe_transaction.data.to,
                "value": safe_transaction.data.value,
                "data": HexBytes(safe_transaction.data.data),
                "operation": safe_transaction.data.operation,
                "safeTxGas": safe_transaction.data.safe_tx_gas,
                "baseGas": safe_transaction.data.base_gas,
                "gasPrice": safe_transaction.data.gas_price,
                "gasToken": safe_transaction.data.gas_token,
                "refundReceiver": safe_transaction.data.refund_receiver,
                "signatures": sorted_signatures,
            }

            tx_params: dict[str, Any] = {"from": self.eth_adapter.get_signer_address()}
            if gas is not None:
                tx_params["gas"] = gas

            tx_hash_hex = self.contract.functions.execTransaction(**params).transact(
                tx_params
            )

            tx_hash = cast(str, tx_hash_hex.hex())

            if wait_for_receipt:
                self.wait_for_transaction(tx_hash)

            return tx_hash
        except Exception as e:
            raise handle_contract_error(e) from e

    def simulate_transaction(self, safe_transaction: SafeTransaction) -> bool:
        """
        Simulates the transaction using eth_call.
        Returns True if the transaction would succeed, False otherwise.
        """
        try:
            params: SafeExecTransactionParams = {
                "to": safe_transaction.data.to,
                "value": safe_transaction.data.value,
                "data": HexBytes(safe_transaction.data.data),
                "operation": safe_transaction.data.operation,
                "safeTxGas": safe_transaction.data.safe_tx_gas,
                "baseGas": safe_transaction.data.base_gas,
                "gasPrice": safe_transaction.data.gas_price,
                "gasToken": safe_transaction.data.gas_token,
                "refundReceiver": safe_transaction.data.refund_receiver,
                "signatures": safe_transaction.sorted_signatures_bytes,
            }

            # Use call() to simulate
            success = self.contract.functions.execTransaction(**params).call(
                {"from": self.eth_adapter.get_signer_address()}
            )

            return cast(bool, success)
        except Exception:
            return False

    def estimate_transaction_gas(self, safe_transaction: SafeTransaction) -> int:
        """
        Estimates the internal gas required for a Safe transaction (safeTxGas).
        Uses the Safe contract's requiredTxGas function.
        """
        params: SafeRequiredTxGasParams = {
            "to": safe_transaction.data.to,
            "value": safe_transaction.data.value,
            "data": HexBytes(safe_transaction.data.data),
            "operation": safe_transaction.data.operation,
            "safeTxGas": safe_transaction.data.safe_tx_gas,
            "baseGas": safe_transaction.data.base_gas,
            "gasPrice": safe_transaction.data.gas_price,
            "gasToken": safe_transaction.data.gas_token,
            "refundReceiver": safe_transaction.data.refund_receiver,
            "signatures": safe_transaction.sorted_signatures_bytes,
        }
        return cast(
            int,
            self.contract.functions.requiredTxGas(**params).call(),
        )

    def estimate_safe_transaction_gas(self, safe_transaction: SafeTransaction) -> int:
        """
        Estimates the total gas (ETH gas) required to execute the Safe transaction.
        Uses eth_estimateGas on the execTransaction function.
        """
        params: SafeExecTransactionParams = {
            "to": safe_transaction.data.to,
            "value": safe_transaction.data.value,
            "data": HexBytes(safe_transaction.data.data),
            "operation": safe_transaction.data.operation,
            "safeTxGas": safe_transaction.data.safe_tx_gas,
            "baseGas": safe_transaction.data.base_gas,
            "gasPrice": safe_transaction.data.gas_price,
            "gasToken": safe_transaction.data.gas_token,
            "refundReceiver": safe_transaction.data.refund_receiver,
            "signatures": safe_transaction.sorted_signatures_bytes,
        }

        return cast(
            int,
            self.contract.functions.execTransaction(**params).estimate_gas(
                {"from": self.eth_adapter.get_signer_address()}
            ),
        )

    def check_signatures(self, safe_transaction: SafeTransaction) -> None:
        """
        Checks if the signatures on the transaction are valid.
        Raises an error if signatures are invalid.
        """
        tx_hash = self.get_transaction_hash(safe_transaction)
        # Convert hex string hash to bytes
        tx_hash_bytes = HexBytes(tx_hash)

        self.contract.functions.checkSignatures(
            tx_hash_bytes,
            HexBytes(safe_transaction.data.data),
            safe_transaction.sorted_signatures_bytes,
        ).call()

    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Any:
        """
        Waits for a transaction receipt.
        """
        return self.eth_adapter.wait_for_transaction_receipt(tx_hash, timeout=timeout)

    def get_domain_separator(self) -> str:
        """
        Returns the EIP-712 domain separator of the Safe.
        """
        return cast(str, self.contract.functions.domainSeparator().call().hex())

    def get_message_hash(self, message: str | bytes) -> str:
        """
        Returns the safe message hash for a given message.
        """
        if isinstance(message, str):
            if message.startswith("0x"):
                message_bytes = HexBytes(message)
            else:
                message_bytes = HexBytes(message.encode("utf-8"))
        elif isinstance(message, bytes):
            message_bytes = HexBytes(message)
        else:
            raise TypeError("message must be str or bytes")

        # keccak256(message)
        from eth_hash.auto import keccak

        message_hash = keccak(message_bytes)

        result = self.contract.functions.getMessageHash(message_hash).call().hex()
        if not result.startswith("0x"):
            result = "0x" + result
        return cast(str, result)

    def sign_message(self, message: str | bytes) -> str:
        """
        Signs a message hash using the current signer.
        Returns the signature using eth_sign (EIP-191).
        """
        message_hash = self.get_message_hash(message)
        return self.eth_adapter.sign_message(message_hash)

    def is_valid_signature(
        self, message_hash: str | bytes, signature: str | bytes
    ) -> bool:
        """
        Checks if a signature is valid for a given message hash using EIP-1271.
        """
        if isinstance(message_hash, str):
            message_hash = HexBytes(message_hash)
        if isinstance(signature, str):
            signature = HexBytes(signature)

        try:
            # isValidSignature(bytes32 _data, bytes memory _signature)
            # returns (bytes4)
            result = self.contract.functions.isValidSignature(
                message_hash, signature
            ).call()
            return HexBytes(result) == HexBytes(EIP1271_MAGIC_VALUE)
        except Exception:
            return False

    def clear_cache(self) -> None:
        """
        Clears the Safe info cache.
        """
        if self._cache:
            self._cache.clear()

    def invalidate_cache(self, key: str) -> None:
        """
        Invalidates a specific cache entry.

        Args:
            key: The cache key to invalidate ("nonce", "threshold", or "owners")
        """
        if self._cache:
            self._cache.invalidate(key)

    def get_signature_count(self, safe_transaction: SafeTransaction) -> int:
        """
        Returns the number of signatures on a Safe transaction.

        Args:
            safe_transaction: The Safe transaction to check

        Returns:
            The number of signatures
        """
        return len(safe_transaction.signatures)

    def has_enough_signatures(self, safe_transaction: SafeTransaction) -> bool:
        """
        Checks if a Safe transaction has enough signatures to be executed.

        Args:
            safe_transaction: The Safe transaction to check

        Returns:
            True if the transaction has enough signatures, False otherwise
        """
        required = self.get_threshold()
        provided = self.get_signature_count(safe_transaction)
        return provided >= required

    def get_missing_signatures(self, safe_transaction: SafeTransaction) -> int:
        """
        Returns the number of missing signatures for a Safe transaction.

        Args:
            safe_transaction: The Safe transaction to check

        Returns:
            The number of missing signatures (0 if enough signatures are present)
        """
        required = self.get_threshold()
        provided = self.get_signature_count(safe_transaction)
        return max(0, required - provided)

    def get_signers(self, safe_transaction: SafeTransaction) -> list[str]:
        """
        Returns the list of addresses that have signed a Safe transaction.

        Args:
            safe_transaction: The Safe transaction to check

        Returns:
            A list of signer addresses
        """
        return sorted(safe_transaction.signatures.keys())
