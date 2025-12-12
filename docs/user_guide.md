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

## Batching Transactions (MultiSend)

You can batch multiple transactions into a single on-chain transaction using `MultiSend`.

```python
from safe_kit.types import SafeTransactionData

# Define multiple transactions
tx1 = SafeTransactionData(to="0xRecipient1", value=100, data="0x")
tx2 = SafeTransactionData(to="0xRecipient2", value=200, data="0x")

# Create a MultiSend transaction
# You need the address of the MultiSend contract on your chain
multi_send_address = "0x..." 
multi_send_tx = safe.create_multi_send_transaction([tx1, tx2], multi_send_address)

# Sign and execute as usual
signed_tx = safe.sign_transaction(multi_send_tx)
tx_hash = safe.execute_transaction(signed_tx)
```

## Using Safe Transaction Service

You can interact with the Safe Transaction Service to propose transactions for other owners to sign.

```python
from safe_kit.service import SafeServiceClient

client = SafeServiceClient("https://safe-transaction-mainnet.safe.global")

# 1. Propose a transaction
safe_tx_hash = safe.get_transaction_hash(signed_tx)
client.propose_transaction(
    safe_address=safe.safe_address,
    safe_tx_data=signed_tx.data,
    safe_tx_hash=safe_tx_hash,
    sender_address=owner.address,
    signature=signed_tx.signatures[owner.address].data.hex()
)

# 2. Get pending transactions
pending_txs = client.get_pending_transactions(safe.safe_address)

# 3. Confirm (sign) a pending transaction
# Assume you are a different owner now
client.confirm_transaction(safe_tx_hash, new_signature)
```

## Deploying a Safe with Custom Modules

You can deploy a new Safe and enable modules during deployment.

```python
from safe_kit.factory import SafeFactory
from safe_kit.types import SafeAccountConfig

factory = SafeFactory(
    eth_adapter=adapter,
    safe_singleton_address="0x...",
    safe_proxy_factory_address="0x..."
)

# To enable a module during deployment, you would typically use a "setup" call
# encoded in the `data` field of SafeAccountConfig.
# However, a simpler way is to deploy first, then enable the module.

# 1. Deploy Safe
config = SafeAccountConfig(
    owners=[owner.address],
    threshold=1
)
safe = factory.deploy_safe(config)
print(f"Deployed Safe at: {safe.safe_address}")

# 2. Enable Module
module_address = "0xModuleAddress"
enable_tx = safe.create_enable_module_transaction(module_address)
signed_tx = safe.sign_transaction(enable_tx)
tx_hash = safe.execute_transaction(signed_tx)
print(f"Module enabled: {tx_hash}")
```
