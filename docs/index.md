# Safe Kit (Python)

A Python implementation of the [Safe Protocol Kit](https://github.com/safe-global/safe-core-sdk), designed to mirror the developer experience of the official Node.js SDK.

## Features

- **DX First**: Intuitive API for interacting with Safe smart accounts.
- **Type Safe**: Built with Pydantic and fully typed for robust development.
- **Modern Stack**: Uses Web3.py, Eth-account, and Python 3.10+.
- **Full Protocol Support**: Supports Safe deployment, transaction creation, signing (EIP-712 & eth_sign), and execution.

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

```bash
pip install safe-kit
```

Or with Poetry:

```bash
poetry add safe-kit
```

## Quick Start

### Initialization

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

For more detailed usage, see the [User Guide](user_guide.md).
