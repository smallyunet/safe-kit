import pytest
from unittest.mock import MagicMock
from safe_kit.safe import Safe
from safe_kit.adapter import Web3Adapter

@pytest.fixture
def mock_adapter():
    adapter = MagicMock(spec=Web3Adapter)
    adapter.get_balance.return_value = 1000
    adapter.get_chain_id.return_value = 1
    adapter.get_signer_address.return_value = "0xSigner"
    return adapter

@pytest.fixture
def mock_contract():
    contract = MagicMock()
    contract.functions.nonce().call.return_value = 5
    contract.functions.getThreshold().call.return_value = 2
    contract.functions.getOwners().call.return_value = ["0xOwner1", "0xOwner2"]
    contract.functions.VERSION().call.return_value = "1.3.0"
    contract.functions.isOwner("0xOwner1").call.return_value = True
    contract.functions.isOwner("0xNotOwner").call.return_value = False
    return contract

@pytest.fixture
def safe(mock_adapter, mock_contract):
    mock_adapter.get_safe_contract.return_value = mock_contract
    return Safe(eth_adapter=mock_adapter, safe_address="0xSafeAddress")

def test_safe_initialization(safe):
    assert safe.get_address() == "0xSafeAddress"

def test_get_balance(safe, mock_adapter):
    assert safe.get_balance() == 1000
    mock_adapter.get_balance.assert_called_with("0xSafeAddress")

def test_get_nonce(safe, mock_contract):
    assert safe.get_nonce() == 5
    mock_contract.functions.nonce().call.assert_called_once()

def test_get_threshold(safe, mock_contract):
    assert safe.get_threshold() == 2
    mock_contract.functions.getThreshold().call.assert_called_once()

def test_get_owners(safe, mock_contract):
    owners = safe.get_owners()
    assert len(owners) == 2
    assert "0xOwner1" in owners
    mock_contract.functions.getOwners().call.assert_called_once()

def test_create_add_owner_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xaddOwnerData"
    
    tx = safe.create_add_owner_transaction("0xNewOwner", 2)
    
    assert tx.data.to == "0xSafeAddress"
    assert tx.data.data == "0xaddOwnerData"
    assert tx.data.value == 0
    assert tx.data.operation == 0
    mock_contract.encodeABI.assert_called_with(
        fn_name="addOwnerWithThreshold",
        args=["0xNewOwner", 2]
    )

def test_create_remove_owner_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xremoveOwnerData"
    # Owners are ["0xOwner1", "0xOwner2"]
    # Removing "0xOwner2", prev should be "0xOwner1"
    
    tx = safe.create_remove_owner_transaction("0xOwner2", 1)
    
    assert tx.data.to == "0xSafeAddress"
    assert tx.data.data == "0xremoveOwnerData"
    mock_contract.encodeABI.assert_called_with(
        fn_name="removeOwner",
        args=["0xOwner1", "0xOwner2", 1]
    )

def test_create_remove_owner_transaction_first_owner(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xremoveOwnerData"
    # Owners are ["0xOwner1", "0xOwner2"]
    # Removing "0xOwner1", prev should be Sentinel
    
    tx = safe.create_remove_owner_transaction("0xOwner1", 1)
    
    mock_contract.encodeABI.assert_called_with(
        fn_name="removeOwner",
        args=["0x0000000000000000000000000000000000000001", "0xOwner1", 1]
    )

def test_create_swap_owner_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xswapOwnerData"
    
    tx = safe.create_swap_owner_transaction("0xOwner2", "0xNewOwner")
    
    mock_contract.encodeABI.assert_called_with(
        fn_name="swapOwner",
        args=["0xOwner1", "0xOwner2", "0xNewOwner"]
    )

def test_create_change_threshold_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xchangeThresholdData"
    
    tx = safe.create_change_threshold_transaction(3)
    
    mock_contract.encodeABI.assert_called_with(
        fn_name="changeThreshold",
        args=[3]
    )
