from __future__ import annotations

from typing import cast

from hexbytes import HexBytes

from .base import SafeContext

EIP1271_MAGIC_VALUE = "0x1626ba7e"


class SafeMessagesMixin(SafeContext):
    def get_domain_separator(self) -> str:
        """Returns the EIP-712 domain separator of the Safe."""
        return cast(str, self.contract.functions.domainSeparator().call().hex())

    def get_message_hash(self, message: str | bytes) -> str:
        """Returns the safe message hash for a given message."""
        if isinstance(message, str):
            if message.startswith("0x"):
                message_bytes = HexBytes(message)
            else:
                message_bytes = HexBytes(message.encode("utf-8"))
        elif isinstance(message, bytes):
            message_bytes = HexBytes(message)
        else:
            raise TypeError("message must be str or bytes")

        from eth_hash.auto import keccak

        message_hash = keccak(message_bytes)

        result = self.contract.functions.getMessageHash(message_hash).call().hex()
        if not result.startswith("0x"):
            result = "0x" + result
        return cast(str, result)

    def sign_message(self, message: str | bytes) -> str:
        """Signs a message hash using the current signer (EIP-191 / eth_sign)."""
        message_hash = self.get_message_hash(message)
        return self.eth_adapter.sign_message(message_hash)

    def is_valid_signature(
        self, message_hash: str | bytes, signature: str | bytes
    ) -> bool:
        """Checks if a signature is valid for a given message hash (EIP-1271)."""
        if isinstance(message_hash, str):
            message_hash = HexBytes(message_hash)
        if isinstance(signature, str):
            signature = HexBytes(signature)

        try:
            result = self.contract.functions.isValidSignature(
                message_hash, signature
            ).call()
            return HexBytes(result) == HexBytes(EIP1271_MAGIC_VALUE)
        except Exception:
            return False
