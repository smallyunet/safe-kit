# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.14] - 2026-01-23

### Added
- **Transaction Builder Pattern**: Added `TransactionBuilder` class with fluent API for creating complex transactions (`safe.tx().send_eth(...).send_erc20(...).build()`).
- **Batch Transaction Helper**: Added `create_batch_transaction` method to `Safe` class for simplified MultiSend transaction creation.
- **Enhanced Error Handling**: Added specific exception classes (`InsufficientSignaturesError`, `InvalidThresholdError`, `OwnerNotFoundError`, `OwnerAlreadyExistsError`, `ModuleNotEnabledError`, `InvalidAddressError`, `TransactionNotFoundError`) for better error messages.
- **Transaction Status Utilities**: Added methods to check transaction status:
  - `get_signature_count`: Get the number of signatures on a transaction
  - `has_enough_signatures`: Check if a transaction has enough signatures
  - `get_missing_signatures`: Get the number of missing signatures
  - `get_signers`: Get the list of addresses that signed a transaction
- **Safe Info Caching**: Added optional caching mechanism for Safe properties (owners, threshold, nonce) to reduce RPC calls:
  - `enable_cache` parameter in `Safe.__init__` to enable caching
  - `cache_ttl` parameter to configure cache expiration time
  - `clear_cache` method to clear all cached data
  - `invalidate_cache` method to invalidate specific cache entries
- **SafeCache Class**: Added standalone cache implementation for time-based value caching.

### Changed
- Enhanced `Safe` class constructor with `enable_cache` and `cache_ttl` parameters.
- Improved error handling with more specific exception types.

## [0.0.13] - 2025-01-10

### Added
- **Chain ID Handling**: Added `get_chain_id` method to `Safe` class for EIP-155 chain ID exposure.
- **Convenience Initialization**: Added `Safe.connect` class method for one-liner Safe initialization with just RPC URL, private key, and Safe address.
- **Adapter Enhancements**: Added `send_transaction` and `get_block` methods to `EthAdapter` for improved low-level control.
- **Factory Wait Option**: Added `wait_for_deployment` parameter to `deploy_safe` and `deploy_safe_v1_4_1` to wait for transaction confirmation.

## [0.0.12] - 2025-12-23

### Added
- **Gas Estimation**: Added `estimate_transaction_gas` and `estimate_safe_transaction_gas` methods to `Safe` class.
- **Gas Control**: Added `gas` parameter to `execute_transaction` for manual gas limit specification.
- **Receipt Waiting**: Added `wait_for_receipt` parameter to `execute_transaction` for blocking execution.
- **Improved Owner Management**: Added validation to prevent adding existing owners or removing non-owners.

## [0.0.11] - 2025-12-23

### Added
- **Pre-validated Signatures**: Added `add_prevalidated_signature` to `Safe` class for signatures where `v=1`.
- **Transaction Simulation**: Added `simulate_transaction` to `Safe` class to test execution success without sending a transaction.
- **Improved Signature Management**: Added `add_signature` helper to `Safe` class for manual signature management.

## [0.0.10] - 2025-12-23

### Added
- **Message Signing**: Added `sign_message` and `get_message_hash` to `Safe` class for EIP-191 message signing.
- **Signature Validation**: Added `is_valid_signature` to `Safe` class for EIP-1271 signature verification.
- **Transaction Waiting**: Added `wait_for_transaction` to `Safe` class and `wait_for_transaction_receipt` to adapters.
- **Transaction Deletion**: Added `delete_transaction` to `SafeServiceClient` to remove pending transactions.

## [0.0.9] - 2025-12-21

### Added
- **Token Info**: Added `get_tokens` and `get_token` to `SafeServiceClient` to fetch supported tokens and token details.
- **Data Decoding**: Added `decode_data` to `SafeServiceClient` to decode transaction data.

## [0.0.8] - 2025-12-21

### Added
- **Safe Info**: Added `get_safe_info` to `SafeServiceClient` to fetch detailed Safe information (owners, threshold, nonce, version, etc.).
- **Creation Info**: Added `get_creation_info` to retrieve Safe creation details (creator, factory, transaction hash).
- **Collectibles**: Added `get_collectibles` to query NFTs (ERC721) owned by a Safe.
- **Delegates Management**: Added `get_delegates`, `add_delegate`, and `remove_delegate` for delegate management.

## [0.0.7] - 2025-12-14

### Added
- **Safe Version Awareness**: Added `get_version` method to `Safe` class.
- **Service Client Enhancements**: Added `get_incoming_transactions` and `get_module_transactions` to `SafeServiceClient`.
- **Address Validation**: Added `is_contract` check and checksum address validation in `Safe` initialization.

## [0.0.6] - 2025-12-13

### Added
- **Transaction History**: Added `get_multisig_transactions` to `SafeServiceClient` to fetch executed transactions with filtering.
- **Chain ID Validation**: Added `chain_id` parameter to `Safe` class constructor to ensure it matches the connected adapter's chain ID.
- **Automated Publishing**: Added GitHub Action to automatically publish to PyPI on tag creation.

## [0.0.3] - 2025-12-12

### Added
- **MultiSend Support**: Added `MultiSend` class and `Safe.create_multi_send_transaction` to batch multiple transactions.
- **Safe Transaction Service**: Added `SafeServiceClient` to interact with the Safe Transaction Service API (propose, confirm, get pending transactions).

### Changed
- Added `requests` dependency.

## [0.0.2] - 2025-10-26

### Added
- Initial implementation of `Safe` class.
- `SafeFactory` for deploying new Safes.
- Support for EIP-712 and `eth_sign` signatures.
- Transaction creation helpers (transfer ETH, ERC20, ERC721).
- Owner management (add, remove, swap, change threshold).
- Basic test suite.
