# User Guide

## Initialization

To start using Safe Kit, you need to initialize a `Safe` instance. This requires a `Web3Adapter` which connects to an Ethereum node and handles signing.

```python
from web3 import Web3
from eth_account import Account
from safe_kit.safe import Safe
from safe_kit.adapter import Web3Adapter

# Setup Web3 and Signer
w3 = Web3(Web3.HTTPProvider("RPC_URL"))
owner = Account.from_key("PRIVATE_KEY")
adapter = Web3Adapter(web3=w3, signer=owner)

# Initialize Safe
safe = Safe(eth_adapter=adapter, safe_address="0xSafeAddress")
```

## Creating and Signing Transactions

You can create transactions to send assets or interact with other contracts.

```python
from safe_kit.types import SafeTransactionData

# Create a transaction (e.g., send ETH)
tx_data = SafeTransactionData(
    to="0xRecipient",
    value=1000000000000000000, # 1 ETH
    data="0x"
)

safe_tx = safe.create_transaction(tx_data)

# Sign the transaction
# Supports "eth_sign_typed_data" (default, EIP-712) or "eth_sign" (legacy)
signed_tx = safe.sign_transaction(safe_tx)
```

## Executing Transactions

Once a transaction has enough signatures (based on the Safe's threshold), it can be executed.

```python
# Execute the transaction on-chain
tx_hash = safe.execute_transaction(signed_tx)
print(f"Transaction executed: {tx_hash}")
```
