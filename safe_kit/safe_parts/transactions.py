from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from hexbytes import HexBytes

from safe_kit.contract_types import (
    SafeApproveHashParams,
    SafeExecTransactionParams,
    SafeGetTransactionHashParams,
    SafeRequiredTxGasParams,
)
from safe_kit.errors import handle_contract_error
from safe_kit.types import SafeTransaction, SafeTransactionData

from .base import SafeContext

if TYPE_CHECKING:
    from safe_kit.builder import TransactionBuilder
    from safe_kit.safe import Safe


class SafeTransactionsMixin(SafeContext):
    def create_transaction(
        self, transaction_data: SafeTransactionData
    ) -> SafeTransaction:
        """Creates a Safe transaction ready to be signed."""
        if transaction_data.nonce is None:
            transaction_data.nonce = self.get_nonce()

        return SafeTransaction(data=transaction_data)

    def tx(self) -> TransactionBuilder:
        """Creates a new TransactionBuilder for fluent transaction creation."""
        from safe_kit.builder import TransactionBuilder

        return TransactionBuilder(cast(Safe, self))

    def create_batch_transaction(
        self,
        transactions: list[SafeTransactionData],
        multisend_address: str = "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
    ) -> SafeTransaction:
        """Creates a batched Safe transaction using MultiSend."""
        from safe_kit.multisend import MultiSend

        encoded_data = MultiSend.encode_transactions(transactions)
        multisend_data = "0x8d80ff0a" + encoded_data.hex()

        batch_tx_data = SafeTransactionData(
            to=multisend_address,
            value=0,
            data=multisend_data,
            operation=1,
        )

        return self.create_transaction(batch_tx_data)

    def sign_transaction(
        self,
        safe_transaction: SafeTransaction,
        method: str = "eth_sign_typed_data",
    ) -> SafeTransaction:
        """Signs a Safe transaction with the current signer."""
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

            sig_bytes = HexBytes(signature)
            r = sig_bytes[:32]
            s = sig_bytes[32:64]
            v = sig_bytes[64] + 4
            signature = (r + s + bytes([v])).hex()
        else:
            raise ValueError(f"Unsupported signing method: {method}")

        safe_transaction.add_signature(signer_address, signature)
        return safe_transaction

    def add_signature(
        self, safe_transaction: SafeTransaction, owner_address: str, signature: str
    ) -> SafeTransaction:
        """Adds a signature to a Safe transaction."""
        owner_address = self.eth_adapter.to_checksum_address(owner_address)
        safe_transaction.add_signature(owner_address, signature)
        return safe_transaction

    def add_prevalidated_signature(
        self, safe_transaction: SafeTransaction, owner_address: str
    ) -> SafeTransaction:
        """Adds a pre-validated signature for a given owner."""
        owner_address = self.eth_adapter.to_checksum_address(owner_address)

        r = owner_address.lower().replace("0x", "").zfill(64)
        s = "0" * 64
        v = "01"
        signature = "0x" + r + s + v

        safe_transaction.add_signature(owner_address, signature)
        return safe_transaction

    def get_transaction_hash(self, safe_transaction: SafeTransaction) -> str:
        """Returns the hash of the Safe transaction."""
        if safe_transaction.data.nonce is None:
            nonce = 0
        else:
            nonce = safe_transaction.data.nonce

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
            "_nonce": nonce,
        }

        return cast(
            str,
            self.contract.functions.getTransactionHash(**params).call().hex(),
        )

    def approve_hash(self, hash_to_approve: str) -> str:
        """Approves a hash on-chain."""
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
        """Executes a Safe transaction."""
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
        """Simulates the transaction using eth_call."""
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

            success = self.contract.functions.execTransaction(**params).call(
                {"from": self.eth_adapter.get_signer_address()}
            )
            return cast(bool, success)
        except Exception:
            return False

    def estimate_transaction_gas(self, safe_transaction: SafeTransaction) -> int:
        """Estimates the internal gas required for a Safe transaction (safeTxGas)."""
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
        return cast(int, self.contract.functions.requiredTxGas(**params).call())

    def estimate_safe_transaction_gas(
        self, safe_transaction: SafeTransaction
    ) -> int:
        """Estimates the total gas required to execute the Safe transaction."""
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
        """Checks if the signatures on the transaction are valid."""
        tx_hash = self.get_transaction_hash(safe_transaction)
        tx_hash_bytes = HexBytes(tx_hash)

        self.contract.functions.checkSignatures(
            tx_hash_bytes,
            HexBytes(safe_transaction.data.data),
            safe_transaction.sorted_signatures_bytes,
        ).call()

    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Any:
        """Waits for a transaction receipt."""
        return self.eth_adapter.wait_for_transaction_receipt(tx_hash, timeout=timeout)

    def get_signature_count(self, safe_transaction: SafeTransaction) -> int:
        """Returns the number of signatures on a Safe transaction."""
        return len(safe_transaction.signatures)

    def has_enough_signatures(self, safe_transaction: SafeTransaction) -> bool:
        """Checks if a Safe transaction has enough signatures to be executed."""
        required = self.get_threshold()
        provided = self.get_signature_count(safe_transaction)
        return provided >= required

    def get_missing_signatures(self, safe_transaction: SafeTransaction) -> int:
        """Returns the number of missing signatures for a Safe transaction."""
        required = self.get_threshold()
        provided = self.get_signature_count(safe_transaction)
        return max(0, required - provided)

    def get_signers(self, safe_transaction: SafeTransaction) -> list[str]:
        """Returns the list of addresses that have signed a Safe transaction."""
        return sorted(safe_transaction.signatures.keys())
