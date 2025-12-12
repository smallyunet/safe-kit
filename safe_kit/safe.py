from typing import Optional, List, Any
from safe_kit.types import SafeTransaction, SafeTransactionData
from safe_kit.adapter import EthAdapter

class Safe:
    """
    The main class for interacting with a Safe.
    """

    def __init__(self, eth_adapter: EthAdapter, safe_address: str):
        self.eth_adapter = eth_adapter
        self.safe_address = safe_address
        self.contract = self.eth_adapter.get_safe_contract(safe_address)

    @classmethod
    def create(cls, eth_adapter: EthAdapter, safe_address: str) -> "Safe":
        """
        Factory method to create a Safe instance.
        """
        return cls(eth_adapter, safe_address)

    def get_address(self) -> str:
        """
        Returns the address of the Safe.
        """
        return self.safe_address

    def get_balance(self) -> int:
        """
        Returns the ETH balance of the Safe.
        """
        return self.eth_adapter.get_balance(self.safe_address)

    def get_nonce(self) -> int:
        """
        Returns the current nonce of the Safe.
        """
        return self.contract.functions.nonce().call()

    def get_threshold(self) -> int:
        """
        Returns the threshold of the Safe.
        """
        return self.contract.functions.getThreshold().call()

    def get_owners(self) -> List[str]:
        """
        Returns the owners of the Safe.
        """
        return self.contract.functions.getOwners().call()

    def get_version(self) -> str:
        """
        Returns the version of the Safe contract.
        """
        return self.contract.functions.VERSION().call()

    def is_owner(self, address: str) -> bool:
        """
        Checks if an address is an owner of the Safe.
        """
        return self.contract.functions.isOwner(address).call()

    def create_transaction(self, transaction_data: SafeTransactionData) -> SafeTransaction:
        """
        Creates a Safe transaction ready to be signed.
        """
        if transaction_data.nonce is None:
            transaction_data.nonce = self.get_nonce()
            
        return SafeTransaction(data=transaction_data)

    def sign_transaction(self, safe_transaction: SafeTransaction) -> SafeTransaction:

        """
        Signs a Safe transaction with the current signer.
        """
        signer_address = self.eth_adapter.get_signer_address()
        if not signer_address:
            raise ValueError("No signer configured in the adapter")

        chain_id = self.eth_adapter.get_chain_id()
        eip712_data = safe_transaction.data.get_eip712_data(chain_id, self.safe_address)
        
        signature = self.eth_adapter.sign_typed_data(eip712_data)
        
        safe_transaction.add_signature(signer_address, signature)
        return safe_transaction

    def execute_transaction(self, safe_transaction: SafeTransaction) -> str:
        """
        Executes a Safe transaction.
        """
        from hexbytes import HexBytes
        
        # Sort signatures
        sorted_signatures = safe_transaction.sorted_signatures_bytes
        
        tx_hash = self.contract.functions.execTransaction(
            safe_transaction.data.to,
            safe_transaction.data.value,
            HexBytes(safe_transaction.data.data),
            safe_transaction.data.operation,
            safe_transaction.data.safe_tx_gas,
            safe_transaction.data.base_gas,
            safe_transaction.data.gas_price,
            safe_transaction.data.gas_token,
            safe_transaction.data.refund_receiver,
            sorted_signatures
        ).transact({"from": self.eth_adapter.get_signer_address()})
        
        return tx_hash.hex()


