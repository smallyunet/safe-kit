import os
import sys
from unittest.mock import MagicMock

from eth_account import Account

# Ensure safe_kit is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from safe_kit import Safe, SafeTransactionData, Web3Adapter  # noqa: E402


def main() -> None:
    # 1. Setup Configuration
    # In a real app, you would connect to a real node,
    # e.g., Web3(Web3.HTTPProvider("..."))
    mock_web3 = MagicMock()
    mock_web3.eth.get_balance.return_value = 1000000000000000000  # 1 ETH
    mock_web3.eth.chain_id = 1  # Mainnet

    # Mock Contract
    mock_contract = MagicMock()
    mock_contract.functions.nonce().call.return_value = 5
    mock_contract.functions.getThreshold().call.return_value = 1
    mock_contract.functions.getOwners().call.return_value = []
    mock_contract.functions.execTransaction().transact.return_value = b"mock_tx_hash"

    mock_web3.eth.contract.return_value = mock_contract

    # Generate a random signer for demonstration

    signer = Account.create()

    print(f"Signer Address: {signer.address}")

    # 2. Initialize Adapter
    adapter = Web3Adapter(web3=mock_web3, signer=signer)

    # 3. Initialize Safe
    safe_address = "0x1234567890123456789012345678901234567890"
    safe = Safe.create(eth_adapter=adapter, safe_address=safe_address)

    print(f"Safe Initialized at: {safe.get_address()}")
    print(f"Safe Balance: {safe.get_balance()} wei")

    # 4. Create a Transaction
    tx_data = SafeTransactionData(
        to="0x0987654321098765432109876543210987654321",
        value=500000000000000000,  # 0.5 ETH
        data="0x",
    )

    print("\nCreating Transaction...")
    safe_tx = safe.create_transaction(tx_data)
    print(f"Transaction created for target: {safe_tx.data.to}")

    # 5. Sign the Transaction
    print("Signing Transaction...")
    signed_tx = safe.sign_transaction(safe_tx)

    print("Transaction Signed!")
    print(f"Signatures: {signed_tx.signatures}")

    # 6. Execute Transaction
    print("\nExecuting Transaction...")
    tx_hash = safe.execute_transaction(signed_tx)
    print(f"Transaction Executed! Hash: {tx_hash}")


if __name__ == "__main__":
    main()
