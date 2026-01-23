"""
Example demonstrating new features in Safe Kit v0.0.14:
- Transaction Builder Pattern
- Batch Transaction Helper
- Transaction Status Checking
- Safe Info Caching
- Enhanced Error Handling
"""
import os
import sys
from unittest.mock import MagicMock

from eth_account import Account

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from safe_kit import (  # noqa: E402
    InsufficientSignaturesError,
    Safe,
    SafeTransactionData,
    Web3Adapter,
)


def setup_mock_environment():
    """Setup mock Web3 environment for demonstration"""
    mock_web3 = MagicMock()
    mock_web3.eth.get_balance.return_value = 5000000000000000000  # 5 ETH
    mock_web3.eth.chain_id = 1
    
    # Mock to_checksum_address to return the address as-is
    mock_web3.to_checksum_address = lambda x: x
    
    # Mock code to indicate address is a contract
    mock_web3.eth.get_code.return_value = b"\x60\x80\x60"  # Non-empty bytecode

    mock_contract = MagicMock()
    mock_contract.functions.nonce().call.return_value = 0
    mock_contract.functions.getThreshold().call.return_value = 2
    mock_contract.functions.getOwners().call.return_value = [
        "0x1111111111111111111111111111111111111111",
        "0x2222222222222222222222222222222222222222",
    ]
    mock_contract.functions.VERSION().call.return_value = "1.3.0"

    mock_web3.eth.contract.return_value = mock_contract

    return mock_web3, mock_contract


def example_transaction_builder():
    """Demonstrate the new TransactionBuilder pattern"""
    print("=" * 60)
    print("EXAMPLE 1: Transaction Builder Pattern")
    print("=" * 60)

    mock_web3, _ = setup_mock_environment()
    signer = Account.create()
    adapter = Web3Adapter(web3=mock_web3, signer=signer)
    safe = Safe(eth_adapter=adapter, safe_address="0x" + "33" * 20)

    # Build a complex batch transaction with fluent API
    print("\nBuilding a batch transaction with fluent API...")
    tx = (
        safe.tx()
        .send_eth("0x" + "44" * 20, 1000000000000000000)  # 1 ETH
        .send_erc20(
            "0x" + "55" * 20,  # Token address
            "0x" + "66" * 20,  # Recipient
            1000,  # Amount
        )
        .send_erc721(
            "0x" + "77" * 20,  # NFT contract
            "0x" + "88" * 20,  # Recipient
            token_id=42,
        )
        .call("0x" + "99" * 20, "0x12345678", value=0)
        .build()
    )

    print(f"✓ Batch transaction created with {safe.tx().transactions.__len__()} ops")
    print(f"  Target: {tx.data.to}")
    print(f"  Operation: {'DelegateCall' if tx.data.operation == 1 else 'Call'}")


def example_batch_helper():
    """Demonstrate the batch transaction helper"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Simplified Batch Transaction")
    print("=" * 60)

    mock_web3, _ = setup_mock_environment()
    signer = Account.create()
    adapter = Web3Adapter(web3=mock_web3, signer=signer)
    safe = Safe(eth_adapter=adapter, safe_address="0x" + "33" * 20)

    # Create multiple transactions
    tx1 = SafeTransactionData(to="0x" + "44" * 20, value=1000000, data="0x")
    tx2 = SafeTransactionData(to="0x" + "55" * 20, value=2000000, data="0x")
    tx3 = SafeTransactionData(to="0x" + "66" * 20, value=3000000, data="0x")

    print("\nCreating batch transaction with helper method...")
    batch_tx = safe.create_batch_transaction([tx1, tx2, tx3])

    print("✓ Batch transaction created")
    print("  Batching 3 transactions into 1")
    print(f"  MultiSend contract: {batch_tx.data.to}")


def example_transaction_status():
    """Demonstrate transaction status checking"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Transaction Status Checking")
    print("=" * 60)

    mock_web3, _ = setup_mock_environment()
    signer = Account.create()
    adapter = Web3Adapter(web3=mock_web3, signer=signer)
    safe = Safe(eth_adapter=adapter, safe_address="0x" + "33" * 20)

    # Create and sign a transaction
    tx_data = SafeTransactionData(to="0x" + "44" * 20, value=1000000, data="0x")
    safe_tx = safe.create_transaction(tx_data)
    signed_tx = safe.sign_transaction(safe_tx)

    print(f"\nSafe threshold: {safe.get_threshold()}")
    print(f"Signature count: {safe.get_signature_count(signed_tx)}")
    print(f"Has enough signatures: {safe.has_enough_signatures(signed_tx)}")
    print(f"Missing signatures: {safe.get_missing_signatures(signed_tx)}")
    print(f"Signers: {safe.get_signers(signed_tx)}")

    if not safe.has_enough_signatures(signed_tx):
        print(f"\n⚠ Need {safe.get_missing_signatures(signed_tx)} more signature(s)")


def example_caching():
    """Demonstrate Safe info caching"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Performance with Caching")
    print("=" * 60)

    mock_web3, mock_contract = setup_mock_environment()
    signer = Account.create()
    adapter = Web3Adapter(web3=mock_web3, signer=signer)

    # Initialize with caching enabled
    print("\nInitializing Safe with caching enabled...")
    safe = Safe(
        eth_adapter=adapter,
        safe_address="0x" + "33" * 20,
        enable_cache=True,
        cache_ttl=60,  # 60 seconds
    )

    print("First calls (will hit RPC):")
    owners1 = safe.get_owners()
    threshold1 = safe.get_threshold()
    nonce1 = safe.get_nonce()
    print(f"  Owners: {len(owners1)} addresses")
    print(f"  Threshold: {threshold1}")
    print(f"  Nonce: {nonce1}")

    # Reset mock call counts
    mock_contract.functions.getOwners().call.reset_mock()
    mock_contract.functions.getThreshold().call.reset_mock()
    mock_contract.functions.nonce().call.reset_mock()

    print("\nSecond calls (will use cache):")
    owners2 = safe.get_owners()
    threshold2 = safe.get_threshold()
    nonce2 = safe.get_nonce()
    print(f"  Owners: {len(owners2)} addresses")
    print(f"  Threshold: {threshold2}")
    print(f"  Nonce: {nonce2}")

    # Verify cache was used (no additional RPC calls)
    owners_calls = mock_contract.functions.getOwners().call.call_count
    threshold_calls = mock_contract.functions.getThreshold().call.call_count
    nonce_calls = mock_contract.functions.nonce().call.call_count
    
    print(f"\n✓ getOwners RPC calls: {owners_calls}")
    print(f"✓ getThreshold RPC calls: {threshold_calls}")
    print(f"✓ nonce RPC calls: {nonce_calls}")

    # Clear cache
    print("\nClearing cache...")
    safe.clear_cache()
    print("✓ Cache cleared")


def example_error_handling():
    """Demonstrate enhanced error handling"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Enhanced Error Handling")
    print("=" * 60)

    mock_web3, _ = setup_mock_environment()
    signer = Account.create()
    adapter = Web3Adapter(web3=mock_web3, signer=signer)
    safe = Safe(eth_adapter=adapter, safe_address="0x" + "33" * 20)

    # Create a transaction with only 1 signature (but threshold is 2)
    tx_data = SafeTransactionData(to="0x" + "44" * 20, value=1000000, data="0x")
    safe_tx = safe.create_transaction(tx_data)
    signed_tx = safe.sign_transaction(safe_tx)

    print(f"\nSafe requires {safe.get_threshold()} signatures")
    print(f"Transaction has {safe.get_signature_count(signed_tx)} signature(s)")

    try:
        # This would fail in real execution
        if not safe.has_enough_signatures(signed_tx):
            required = safe.get_threshold()
            provided = safe.get_signature_count(signed_tx)
            raise InsufficientSignaturesError(required=required, provided=provided)
    except InsufficientSignaturesError as e:
        print(f"\n✓ Caught specific error: {type(e).__name__}")
        print(f"  Message: {e}")
        print(f"  Required: {e.required}")
        print(f"  Provided: {e.provided}")


def main():
    print("\n" + "=" * 60)
    print("Safe Kit v0.0.14 - New Features Demo")
    print("=" * 60)

    example_transaction_builder()
    example_batch_helper()
    example_transaction_status()
    example_caching()
    example_error_handling()

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
