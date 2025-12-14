# Roadmap

This document outlines the development roadmap for `safe-kit` and tracks its feature parity with the official [Safe Protocol Kit](https://github.com/safe-global/safe-core-sdk/tree/main/packages/protocol-kit).

## Release Plan

### v0.0.x (Alpha)
Focus on implementing core functionalities and ensuring the library is usable for basic operations.

- **v0.0.2** (Released): Basic Safe deployment, transaction creation, and execution.
- **v0.0.3** (Released): MultiSend support (batching) and Safe Transaction Service integration.
- **v0.0.4** (Released): Improved type safety, auto-generated types from ABIs, and CI/CD integration.
- **v0.0.5** (Skipped): Implementation merged into v0.0.6.
- **v0.0.6** (Released): Enhanced Safe Transaction Service client (history), Chain ID validation, and automated PyPI publishing.
- **v0.0.7** (Released): Safe version awareness, extended service client queries, and improved address validation.

### v0.1.x (Beta)
Focus on stability, comprehensive testing, and developer experience improvements.

- **v0.1.0**: Full test coverage (including integration tests with local nodes), improved error handling, and documentation polish.

### v1.0.0 (Stable)
Production-ready release with stable API and full feature parity.

---

## Feature Parity Status

### 1. Safe Factory (Deployment)
*Status: Implemented*

- [x] **`SafeFactory` Class**: Create a factory class to handle Safe deployments.
- [x] **`deploySafe`**: Method to deploy a new Safe with initial configuration.
- [x] **`predictSafeAddress`**: Calculate counterfactual address.
- [x] **Safe Proxy Factory**: Integration with Safe Proxy Factory.

### 2. Safe Management
*Status: Implemented*

- [x] **Owner Management**: Add, remove, and swap owners (`addOwnerWithThreshold`, etc.).
- [x] **Threshold Management**: Change signature threshold (`changeThreshold`).

### 3. Transaction Helpers
*Status: Implemented*

- [x] **Transfers**: ETH (`createNativeTransferTx`), ERC20 (`createERC20TransferTx`), ERC721 (`createERC721TransferTx`).
- [x] **Modules**: Enable/Disable modules (`createEnableModuleTx`, `createDisableModuleTx`).
- [x] **Rejection**: Cancel pending transactions (`createRejectionTx`).

### 4. Signatures & Execution
*Status: Implemented*

- [x] **EIP-712 Signatures**: Standard Safe signature format.
- [x] **`eth_sign` Support**: Legacy signature support.
- [x] **On-chain Approval**: `approveHash` for smart contract wallets.
- [x] **Signature Validation**: Off-chain validation via `checkSignatures`.
- [x] **Gas Estimation**: Automatic `safeTxGas` calculation.

### 5. Advanced Features
*Status: Partially Implemented*

- [x] **Modules**: Query enabled modules (`getModules`, `isModuleEnabled`).
- [x] **Guards**: Transaction guards (`getGuard`, `setGuardTx`).
- [x] **Fallback Handler**: Fallback handler management (`getFallbackHandler`, `setFallbackHandlerTx`).
- [x] **MultiSend**: Batch multiple transactions into one (Added in v0.0.3).
- [ ] **Multi-version Support**: Compatibility with older Safe versions (v1.0.0 - v1.2.0).

### 6. Service Integration
*Status: Implemented*

- [x] **Safe Transaction Service**: Client for `propose_transaction`, `confirm_transaction`, etc. (Added in v0.0.3).

### 7. Infrastructure & DX
*Status: In Progress*

- [x] **Error Handling**: Readable Python exceptions for EVM reverts.
- [x] **Type Generation**: Auto-generate Python types from Safe ABIs.
- [x] **CI/CD**: Automated linting, testing, and type checking.
- [ ] **Chain ID Handling**: Better support for EIP-155.
- [ ] **Automated Publishing**: Publish to PyPI on release.
