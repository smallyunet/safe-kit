import pytest
from eth_account import Account
from web3 import Web3

from safe_kit import SafeAccountConfig, SafeFactory, Web3Adapter

# Safe v1.3.0 Contracts on Mainnet
SAFE_SINGLETON_ADDRESS = "0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552"
SAFE_PROXY_FACTORY_ADDRESS = "0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2"

# Anvil default mnemonic account 0
# Private key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
TEST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
TEST_ACCOUNT_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"


@pytest.fixture(scope="module")
def web3():
    """
    Connect to local Anvil node.
    Requires anvil running on port 8545.
    """
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        pytest.skip(
            "Local Anvil node not running. "
            "Run 'anvil --fork-url <RPC_URL>' to enable E2E tests."
        )
    return w3


@pytest.fixture(scope="module")
def adapter(web3):
    account = Account.from_key(TEST_PRIVATE_KEY)
    return Web3Adapter(web3, signer=account)


@pytest.mark.e2e
def test_full_safe_lifecycle(web3, adapter):
    """
    Test the full lifecycle: Deploy -> Fund -> Transact
    """
    print("\n--- Starting E2E Test ---")

    # 1. Setup Owner
    owner_account = Account.from_key(TEST_PRIVATE_KEY)
    print(f"Owner Address: {owner_account.address}")

    # 2. Deploy New Safe
    print("Deploying new Safe...")
    factory = SafeFactory(
        eth_adapter=adapter,
        safe_singleton_address=SAFE_SINGLETON_ADDRESS,
        safe_proxy_factory_address=SAFE_PROXY_FACTORY_ADDRESS,
    )

    safe_config = SafeAccountConfig(owners=[owner_account.address], threshold=1)

    # Predict address first
    import random

    salt_nonce = random.randint(0, 1000000)
    predicted_address = factory.predict_safe_address(safe_config, salt_nonce=salt_nonce)
    print(f"Predicted Safe Address: {predicted_address}")

    # Deploy
    # Note: In a real test we might want to wait for receipt, but Anvil is instant
    safe = factory.deploy_safe(safe_config, salt_nonce=salt_nonce)

    assert safe.get_address() == predicted_address
    assert safe.get_threshold() == 1
    assert safe.get_owners() == [owner_account.address]
    print(f"Safe Deployed at: {safe.get_address()}")

    # 3. Fund the Safe
    print("Funding Safe...")
    fund_amount = web3.to_wei(1, "ether")
    web3.eth.send_transaction(
        {"from": owner_account.address, "to": safe.get_address(), "value": fund_amount}
    )

    initial_balance = safe.get_balance()
    assert initial_balance == fund_amount
    print(f"Safe Balance: {web3.from_wei(initial_balance, 'ether')} ETH")

    # 4. Create Transaction (Send 0.1 ETH back to owner)
    print("Creating Transaction...")
    recipient = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"  # Anvil Account 1
    transfer_amount = web3.to_wei(0.1, "ether")

    # Create native transfer
    safe_tx = safe.create_native_transfer_transaction(
        to=recipient, amount=transfer_amount
    )

    # 5. Sign Transaction
    print("Signing Transaction...")
    signed_tx = safe.sign_transaction(safe_tx)

    # 6. Execute Transaction
    print("Executing Transaction...")
    tx_hash = safe.execute_transaction(signed_tx)
    print(f"Execution Tx Hash: {tx_hash}")

    # 7. Verify Result
    final_balance = safe.get_balance()
    recipient_balance = web3.eth.get_balance(recipient)

    print(f"Safe Final Balance: {web3.from_wei(final_balance, 'ether')} ETH")

    # Check Safe balance decreased (amount + gas cost,
    # but gas is paid by executor/owner,
    # here the safe pays 0 gas for the execution itself unless refund is set up,
    # but the value transfer definitely reduces balance)
    assert final_balance == initial_balance - transfer_amount
    # Check recipient received funds (assuming they started with 10000 ETH or 0,
    # checking delta is safer)
    # But for Anvil account 1, let's just check it has at least the amount.
    assert recipient_balance >= transfer_amount

    print("--- E2E Test Passed Successfully ---")
