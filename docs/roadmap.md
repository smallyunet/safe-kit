# Safe Kit Roadmap & Feature Parity Status

This document outlines the roadmap for `safe-kit` to achieve feature parity with the official [Safe Protocol Kit](https://github.com/safe-global/safe-core-sdk/tree/main/packages/protocol-kit).

## 1. Safe Factory (Deployment)
*Current Status: Implemented*

The ability to deploy new Safe contracts is implemented via `SafeFactory`.

- [x] **`SafeFactory` Class**: Create a factory class to handle Safe deployments.
- [x] **`deploySafe`**: Method to deploy a new Safe with initial configuration (owners, threshold, etc.).
- [x] **`predictSafeAddress`**: Method to calculate the counterfactual address of a Safe before deployment.
- [x] **Support for Safe Proxy Factory**: Integrate with the Safe Proxy Factory contract.

## 2. Safe Management (Owners & Thresholds)
*Current Status: Implemented*

We can now create transactions to manage owners and thresholds.

- [x] **`addOwnerWithThreshold`**: Create a transaction to add a new owner and optionally update the threshold.
- [x] **`removeOwner`**: Create a transaction to remove an owner and update the threshold.
- [x] **`swapOwner`**: Create a transaction to replace an existing owner with a new one.
- [x] **`changeThreshold`**: Create a transaction to change the signature threshold.

## 3. Transaction Creation Helpers
*Current Status: Implemented*

Helper methods for creating common transactions are now available.

- [x] **`createEnableModuleTx`**: Helper to enable a Safe module.
- [x] **`createDisableModuleTx`**: Helper to disable a Safe module.
- [x] **`createAddOwnerTx`**: Helper for owner management (underlying logic for section 2).
- [x] **`createERC20TransferTx`**: Helper to create a standard ERC20 token transfer.
- [x] **`createERC721TransferTx`**: Helper to create an NFT transfer.
- [x] **`createNativeTransferTx`**: Helper for ETH/Native token transfers.
- [x] **`createRejectionTx`**: Helper to create a transaction with the same nonce (to cancel a pending tx).

## 4. Signatures & Execution
*Current Status: Implemented*

- [x] **`approveHash`**: Support for on-chain transaction approval (for smart contract wallets as owners).
- [x] **`eth_sign` Support**: Support for `eth_sign` (legacy) signatures for hardware wallets that don't support EIP-712.
- [x] **Signature Validation**: Utilities to verify signatures off-chain (via `checkSignatures`).
- [x] **Gas Estimation**: `estimateTxGas` to automatically calculate `safeTxGas` (via `requiredTxGas`).

## 5. Advanced Features
*Current Status: Implemented*

- [x] **Modules**: `getModules`, `isModuleEnabled` (Implemented in Section 3).
- [x] **Guards**: `getGuard`, `setGuardTx`.
- [x] **Fallback Handler**: `getFallbackHandler`, `setFallbackHandlerTx`.
- [ ] **Multi-version Support**: Ensure compatibility with Safe contracts v1.0.0, v1.1.1, v1.2.0, v1.3.0, v1.4.1.

## 6. Infrastructure & DX
- [ ] **Type Generation**: Auto-generate Python types from Safe ABIs.
- [ ] **Chain ID Handling**: Better support for EIP-155 and chain-specific logic.
- [x] **Error Handling**: Parse EVM revert reasons into readable Python exceptions.
