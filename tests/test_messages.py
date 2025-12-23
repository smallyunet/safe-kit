from unittest.mock import MagicMock

import pytest
from hexbytes import HexBytes

from safe_kit.adapter import Web3Adapter
from safe_kit.safe import Safe


@pytest.fixture
def mock_adapter():
    adapter = MagicMock(spec=Web3Adapter)
    adapter.to_checksum_address.side_effect = lambda x: x
    return adapter


@pytest.fixture
def safe(mock_adapter):
    mock_adapter.is_contract.return_value = True
    return Safe(mock_adapter, "0xSafeAddress")


def test_get_message_hash(safe):
    message = "Hello World"
    # Expected hash for "Hello World"
    # This depends on how getMessageHash is implemented in the contract, 
    # but strictly speaking, get_message_hash in Safe class calls the contract.
    # We should mock the contract call.
    
    expected_hash = (
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )
    safe.contract.functions.getMessageHash.return_value.call.return_value = (
        HexBytes(expected_hash)
    )

    assert safe.get_message_hash(message) == expected_hash


def test_sign_message(safe):
    message = "Hello World"
    message_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    signature = "0xabcdef1234567890"

    safe.get_message_hash = MagicMock(return_value=message_hash)
    safe.eth_adapter.sign_message.return_value = signature

    assert safe.sign_message(message) == signature
    safe.eth_adapter.sign_message.assert_called_with(message_hash)


def test_is_valid_signature_true(safe):
    message_hash = (
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )
    signature = "0xabcdef1234567890"
    magic_value = "0x1626ba7e"  # EIP1271_MAGIC_VALUE

    safe.contract.functions.isValidSignature.return_value.call.return_value = (
        HexBytes(magic_value)
    )

    assert safe.is_valid_signature(message_hash, signature) is True


def test_is_valid_signature_false(safe):
    message_hash = (
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )
    signature = "0xabcdef1234567890"

    safe.contract.functions.isValidSignature.return_value.call.return_value = (
        HexBytes("0x00000000")
    )

    assert safe.is_valid_signature(message_hash, signature) is False


def test_wait_for_transaction(safe):
    tx_hash = "0xtxhash"
    receipt = {"status": 1}
    
    safe.eth_adapter.wait_for_transaction_receipt.return_value = receipt
    
    assert safe.wait_for_transaction(tx_hash) == receipt
    safe.eth_adapter.wait_for_transaction_receipt.assert_called_with(
        tx_hash, timeout=120
    )
