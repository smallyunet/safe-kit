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

    def _get_previous_owner(self, owner: str) -> str:
        owners = self.get_owners()
        try:
            index = owners.index(owner)
        except ValueError:
            raise ValueError(f"Address {owner} is not an owner")
        
        if index == 0:
            return "0x0000000000000000000000000000000000000001" # Sentinel
        return owners[index - 1]

    def create_add_owner_transaction(self, owner: str, threshold: Optional[int] = None) -> SafeTransaction:
        """
        Creates a transaction to add a new owner to the Safe.
        """
        if threshold is None:
            threshold = self.get_threshold()
            
        data = self.contract.encodeABI(
            fn_name="addOwnerWithThreshold",
            args=[owner, threshold]
        )
        
        return self.create_transaction(SafeTransactionData(
            to=self.safe_address,
            value=0,
            data=data,
            operation=0
        ))

    def create_remove_owner_transaction(self, owner: str, threshold: Optional[int] = None) -> SafeTransaction:
        """
        Creates a transaction to remove an owner from the Safe.
        """
        if threshold is None:
            threshold = self.get_threshold()
            
        prev_owner = self._get_previous_owner(owner)
        
        data = self.contract.encodeABI(
            fn_name="removeOwner",
            args=[prev_owner, owner, threshold]
        )
        
        return self.create_transaction(SafeTransactionData(
            to=self.safe_address,
            value=0,
            data=data,
            operation=0
        ))

    def create_swap_owner_transaction(self, old_owner: str, new_owner: str) -> SafeTransaction:
        """
        Creates a transaction to replace an existing owner with a new one.
        """
        prev_owner = self._get_previous_owner(old_owner)
        
        data = self.contract.encodeABI(
            fn_name="swapOwner",
            args=[prev_owner, old_owner, new_owner]
        )
        
        return self.create_transaction(SafeTransactionData(
            to=self.safe_address,
            value=0,
            data=data,
            operation=0
        ))

    def create_change_threshold_transaction(self, threshold: int) -> SafeTransaction:
        """
        Creates a transaction to change the threshold of the Safe.
        """
        data = self.contract.encodeABI(
            fn_name="changeThreshold",
            args=[threshold]
        )
        
        return self.create_transaction(SafeTransactionData(
            to=self.safe_address,
            value=0,
            data=data,
            operation=0
        ))

    def get_modules(self) -> List[str]:
        """
        Returns the modules enabled on the Safe.
        """
        # Sentinel address for modules
        start = "0x0000000000000000000000000000000000000001"
        page_size = 10
        modules = []
        
        while True:
            array, next_module = self.contract.functions.getModulesPaginated(start, page_size).call()
            modules.extend(array)
            
            if next_module == "0x0000000000000000000000000000000000000001" or next_module == "0x0000000000000000000000000000000000000000":
                break
            start = next_module
            
        return modules

    def is_module_enabled(self, module_address: str) -> bool:
        """
        Checks if a module is enabled on the Safe.
        """
        return self.contract.functions.isModuleEnabled(module_address).call()

    def create_enable_module_transaction(self, module_address: str) -> SafeTransaction:
        """
        Creates a transaction to enable a Safe module.
        """
        data = self.contract.encodeABI(
            fn_name="enableModule",
            args=[module_address]
        )
        
        return self.create_transaction(SafeTransactionData(
            to=self.safe_address,
            value=0,
            data=data,
            operation=0
        ))

    def create_disable_module_transaction(self, module_address: str) -> SafeTransaction:
        """
        Creates a transaction to disable a Safe module.
        """
        modules = self.get_modules()
        try:
            index = modules.index(module_address)
        except ValueError:
            raise ValueError(f"Module {module_address} is not enabled")
            
        if index == 0:
            prev_module = "0x0000000000000000000000000000000000000001"
        else:
            prev_module = modules[index - 1]
            
        data = self.contract.encodeABI(
            fn_name="disableModule",
            args=[prev_module, module_address]
        )
        
        return self.create_transaction(SafeTransactionData(
            to=self.safe_address,
            value=0,
            data=data,
            operation=0
        ))

    def create_erc20_transfer_transaction(self, token_address: str, to: str, amount: int) -> SafeTransaction:
        """
        Creates a transaction to transfer ERC20 tokens.
        """
        from safe_kit.abis import ERC20_ABI
        token_contract = self.eth_adapter.get_contract(token_address, ERC20_ABI)
        
        data = token_contract.encodeABI(
            fn_name="transfer",
            args=[to, amount]
        )
        
        return self.create_transaction(SafeTransactionData(
            to=token_address,
            value=0,
            data=data,
            operation=0
        ))

    def create_erc721_transfer_transaction(self, token_address: str, to: str, token_id: int) -> SafeTransaction:
        """
        Creates a transaction to transfer ERC721 tokens.
        """
        from safe_kit.abis import ERC721_ABI
        token_contract = self.eth_adapter.get_contract(token_address, ERC721_ABI)
        
        data = token_contract.encodeABI(
            fn_name="safeTransferFrom",
            args=[self.safe_address, to, token_id]
        )
        
        return self.create_transaction(SafeTransactionData(
            to=token_address,
            value=0,
            data=data,
            operation=0
        ))

    def create_native_transfer_transaction(self, to: str, amount: int) -> SafeTransaction:
        """
        Creates a transaction to transfer native tokens (ETH).
        """
        return self.create_transaction(SafeTransactionData(
            to=to,
            value=amount,
            data="0x",
            operation=0
        ))

    def create_rejection_transaction(self, nonce: int) -> SafeTransaction:
        """
        Creates a transaction to reject a pending transaction (by reusing the nonce).
        """
        return self.create_transaction(SafeTransactionData(
            to=self.safe_address,
            value=0,
            data="0x",
            operation=0,
            nonce=nonce
        ))


