# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
