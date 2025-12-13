from unittest.mock import MagicMock

import pytest

from safe_kit.adapter import Web3Adapter
from safe_kit.safe import Safe
from safe_kit.types import SafeTransactionData


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


def test_safe_initialization_chain_id_match(mock_adapter, mock_contract):
    # Adapter defaults to chain_id=1
    mock_adapter.get_safe_contract.return_value = mock_contract
    safe = Safe(eth_adapter=mock_adapter, safe_address="0xSafeAddress", chain_id=1)
    assert safe.chain_id == 1


def test_safe_initialization_chain_id_mismatch(mock_adapter, mock_contract):
    # Adapter defaults to chain_id=1
    mock_adapter.get_safe_contract.return_value = mock_contract
    with pytest.raises(ValueError, match="Adapter chain ID \(1\) does not match Safe chain ID \(2\)"):
        Safe(eth_adapter=mock_adapter, safe_address="0xSafeAddress", chain_id=2)


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
        fn_name="addOwnerWithThreshold", args=["0xNewOwner", 2]
    )


def test_create_remove_owner_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xremoveOwnerData"
    # Owners are ["0xOwner1", "0xOwner2"]
    # Removing "0xOwner2", prev should be "0xOwner1"

    tx = safe.create_remove_owner_transaction("0xOwner2", 1)

    assert tx.data.to == "0xSafeAddress"
    assert tx.data.data == "0xremoveOwnerData"
    mock_contract.encodeABI.assert_called_with(
        fn_name="removeOwner", args=["0xOwner1", "0xOwner2", 1]
    )


def test_create_remove_owner_transaction_first_owner(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xremoveOwnerData"
    # Owners are ["0xOwner1", "0xOwner2"]
    # Removing "0xOwner1", prev should be Sentinel

    safe.create_remove_owner_transaction("0xOwner1", 1)

    mock_contract.encodeABI.assert_called_with(
        fn_name="removeOwner",
        args=["0x0000000000000000000000000000000000000001", "0xOwner1", 1],
    )


def test_create_swap_owner_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xswapOwnerData"

    safe.create_swap_owner_transaction("0xOwner2", "0xNewOwner")

    mock_contract.encodeABI.assert_called_with(
        fn_name="swapOwner", args=["0xOwner1", "0xOwner2", "0xNewOwner"]
    )


def test_get_transaction_hash(safe, mock_contract):
    mock_contract.functions.getTransactionHash.return_value.call.return_value = b"hash"

    tx = safe.create_native_transfer_transaction("0xReceiver", 100)
    tx_hash = safe.get_transaction_hash(tx)

    assert tx_hash == "68617368"  # hex of b"hash"
    mock_contract.functions.getTransactionHash.assert_called_once()


def test_approve_hash(safe, mock_contract, mock_adapter):
    mock_contract.functions.approveHash.return_value.transact.return_value = b"tx_hash"

    # Use a valid hex string
    tx_hash = safe.approve_hash(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )

    assert tx_hash == "74785f68617368"  # hex of b"tx_hash"
    mock_contract.functions.approveHash.assert_called_once()


def test_sign_transaction_eth_sign(safe, mock_adapter, mock_contract):
    mock_contract.functions.getTransactionHash.return_value.call.return_value = b"hash"
    # Mock signature: r(32) + s(32) + v(1)
    # v=27 (0x1b) -> +4 -> 31 (0x1f)
    mock_signature = b"\x00" * 64 + b"\x1b"
    mock_adapter.sign_message.return_value = mock_signature

    tx = safe.create_native_transfer_transaction("0xReceiver", 100)
    signed_tx = safe.sign_transaction(tx, method="eth_sign")

    expected_signature = (b"\x00" * 64 + b"\x1f").hex()
    assert signed_tx.signatures["0xSigner"] == expected_signature
    mock_adapter.sign_message.assert_called_with("68617368")


def test_create_change_threshold_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xchangeThresholdData"

    safe.create_change_threshold_transaction(3)

    mock_contract.encodeABI.assert_called_with(fn_name="changeThreshold", args=[3])


def test_get_modules(safe, mock_contract):
    # Mock pagination: first call returns [mod1], next=mod1;
    # second call returns [mod2], next=sentinel
    mock_contract.functions.getModulesPaginated.side_effect = [
        MagicMock(call=MagicMock(return_value=(["0xMod1"], "0xMod1"))),
        MagicMock(
            call=MagicMock(
                return_value=(["0xMod2"], "0x0000000000000000000000000000000000000001")
            )
        ),
    ]

    modules = safe.get_modules()

    assert modules == ["0xMod1", "0xMod2"]
    assert mock_contract.functions.getModulesPaginated.call_count == 2


def test_is_module_enabled(safe, mock_contract):
    mock_contract.functions.isModuleEnabled("0xMod1").call.return_value = True
    assert safe.is_module_enabled("0xMod1") is True


def test_create_enable_module_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xenableModuleData"

    tx = safe.create_enable_module_transaction("0xMod1")

    assert tx.data.data == "0xenableModuleData"
    mock_contract.encodeABI.assert_called_with(fn_name="enableModule", args=["0xMod1"])


def test_create_disable_module_transaction(safe, mock_contract):
    # Mock get_modules to return ["0xMod1", "0xMod2"]
    # We want to disable "0xMod2", so prev should be "0xMod1"
    mock_contract.functions.getModulesPaginated.side_effect = [
        MagicMock(
            call=MagicMock(
                return_value=(
                    ["0xMod1", "0xMod2"],
                    "0x0000000000000000000000000000000000000001",
                )
            )
        )
    ]
    mock_contract.encodeABI.return_value = "0xdisableModuleData"

    tx = safe.create_disable_module_transaction("0xMod2")

    assert tx.data.data == "0xdisableModuleData"
    mock_contract.encodeABI.assert_called_with(
        fn_name="disableModule", args=["0xMod1", "0xMod2"]
    )


def test_create_erc20_transfer_transaction(safe, mock_adapter):
    mock_token = MagicMock()
    mock_token.encodeABI.return_value = "0xerc20TransferData"
    mock_adapter.get_contract.return_value = mock_token

    tx = safe.create_erc20_transfer_transaction("0xToken", "0xReceiver", 100)

    assert tx.data.to == "0xToken"
    assert tx.data.data == "0xerc20TransferData"
    assert tx.data.value == 0
    mock_token.encodeABI.assert_called_with(
        fn_name="transfer", args=["0xReceiver", 100]
    )


def test_create_erc721_transfer_transaction(safe, mock_adapter):
    mock_token = MagicMock()
    mock_token.encodeABI.return_value = "0xerc721TransferData"
    mock_adapter.get_contract.return_value = mock_token

    tx = safe.create_erc721_transfer_transaction("0xNFT", "0xReceiver", 1)

    assert tx.data.to == "0xNFT"
    assert tx.data.data == "0xerc721TransferData"
    assert tx.data.value == 0
    mock_token.encodeABI.assert_called_with(
        fn_name="safeTransferFrom", args=["0xSafeAddress", "0xReceiver", 1]
    )


def test_create_native_transfer_transaction(safe):
    tx = safe.create_native_transfer_transaction("0xReceiver", 100)

    assert tx.data.to == "0xReceiver"
    assert tx.data.value == 100
    assert tx.data.data == "0x"


def test_create_rejection_transaction(safe):
    tx = safe.create_rejection_transaction(5)

    assert tx.data.to == "0xSafeAddress"
    assert tx.data.value == 0
    assert tx.data.data == "0x"
    assert tx.data.nonce == 5


def test_estimate_transaction_gas(safe, mock_contract):
    mock_contract.functions.requiredTxGas.return_value.call.return_value = 50000

    tx = safe.create_native_transfer_transaction("0xReceiver", 100)
    gas = safe.estimate_transaction_gas(tx)

    assert gas == 50000
    mock_contract.functions.requiredTxGas.assert_called_once()


def test_check_signatures(safe, mock_contract):
    mock_contract.functions.getTransactionHash.return_value.call.return_value = b"hash"

    tx = safe.create_native_transfer_transaction("0xReceiver", 100)
    # Should not raise
    safe.check_signatures(tx)

    mock_contract.functions.checkSignatures.assert_called_once()


def test_get_guard(safe, mock_adapter):
    # Mock storage return value (padded address)
    mock_adapter.get_storage_at.return_value = b"\x00" * 12 + b"\x12" * 20

    guard = safe.get_guard()

    assert guard == "0x" + "12" * 20
    mock_adapter.get_storage_at.assert_called_with(
        "0xSafeAddress",
        0x4A204F620C8C5CCDCA3FD54D003B6D13435454A733A569F8E4A6426EA62BF7A0,
    )


def test_create_set_guard_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xsetGuardData"

    tx = safe.create_set_guard_transaction("0xGuard")

    assert tx.data.data == "0xsetGuardData"
    mock_contract.encodeABI.assert_called_with(fn_name="setGuard", args=["0xGuard"])


def test_get_fallback_handler(safe, mock_adapter):
    # Mock storage return value (padded address)
    mock_adapter.get_storage_at.return_value = b"\x00" * 12 + b"\x34" * 20

    handler = safe.get_fallback_handler()

    assert handler == "0x" + "34" * 20
    mock_adapter.get_storage_at.assert_called_with(
        "0xSafeAddress",
        0x6C9A6C4A39284E37ED1CF53D337577D14212A4870FB976A4366C693B939918D5,
    )


def test_create_set_fallback_handler_transaction(safe, mock_contract):
    mock_contract.encodeABI.return_value = "0xsetFallbackHandlerData"

    tx = safe.create_set_fallback_handler_transaction("0xHandler")

    assert tx.data.data == "0xsetFallbackHandlerData"
    mock_contract.encodeABI.assert_called_with(
        fn_name="setFallbackHandler", args=["0xHandler"]
    )


def test_sign_transaction_eth_sign_manual(safe, mock_adapter, mock_contract):
    # Mock transaction data
    tx_data = SafeTransactionData(to="0xTo", value=0, data="0x", operation=0, nonce=0)
    safe_tx = safe.create_transaction(tx_data)

    # Mock getTransactionHash
    # Return bytes directly as web3.py call() would return bytes for bytes32
    mock_contract.functions.getTransactionHash.return_value.call.return_value = (
        b"\x01" * 32
    )

    # Mock sign_message return value (65 bytes hex)
    # r(32) + s(32) + v(1)
    # v=27 (0x1b)
    mock_adapter.sign_message.return_value = "00" * 32 + "00" * 32 + "1b"

    signed_tx = safe.sign_transaction(safe_tx, method="eth_sign")

    # Check if sign_message was called
    mock_adapter.sign_message.assert_called()

    # Check if signature was added and modified
    # v should be 27 + 4 = 31 (0x1f)
    expected_sig = "00" * 32 + "00" * 32 + "1f"
    assert signed_tx.signatures["0xSigner"] == expected_sig
