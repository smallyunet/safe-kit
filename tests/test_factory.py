from unittest.mock import MagicMock

import pytest

from safe_kit.adapter import Web3Adapter
from safe_kit.factory import SafeFactory
from safe_kit.types import SafeAccountConfig


@pytest.fixture
def mock_adapter():
    adapter = MagicMock(spec=Web3Adapter)
    adapter.get_signer_address.return_value = "0xSigner"
    adapter.to_checksum_address.side_effect = lambda x: x
    adapter.is_contract.return_value = True
    return adapter


@pytest.fixture
def mock_proxy_factory(mock_adapter):
    contract = MagicMock()
    mock_adapter.get_contract.return_value = contract
    return contract


@pytest.fixture
def mock_safe_singleton(mock_adapter):
    contract = MagicMock()
    mock_adapter.get_safe_contract.return_value = contract
    return contract


@pytest.fixture
def factory(mock_adapter, mock_proxy_factory, mock_safe_singleton):
    return SafeFactory(
        eth_adapter=mock_adapter,
        safe_singleton_address="0xSingleton",
        safe_proxy_factory_address="0xFactory",
    )


def test_predict_safe_address(factory, mock_proxy_factory, mock_safe_singleton):
    mock_safe_singleton.encodeABI.return_value = b"initializer"
    mock_proxy_factory.functions.createProxyWithNonce.return_value.call.return_value = (
        "0xPredictedSafe"
    )

    config = SafeAccountConfig(owners=["0xOwner1"], threshold=1)
    address = factory.predict_safe_address(config)

    assert address == "0xPredictedSafe"
    mock_safe_singleton.encodeABI.assert_called_once()
    mock_proxy_factory.functions.createProxyWithNonce.assert_called_with(
        _singleton="0xSingleton", initializer=b"initializer", saltNonce=0
    )


def test_deploy_safe(factory, mock_proxy_factory, mock_safe_singleton):
    mock_safe_singleton.encodeABI.return_value = b"initializer"
    mock_proxy_factory.functions.createProxyWithNonce.return_value.call.return_value = (
        "0xPredictedSafe"
    )

    config = SafeAccountConfig(owners=["0xOwner1"], threshold=1)
    safe = factory.deploy_safe(config)

    assert safe.get_address() == "0xPredictedSafe"
    mock_proxy_factory.functions.createProxyWithNonce.return_value.transact.assert_called_with(
        {"from": "0xSigner"}
    )
    mock_proxy_factory.functions.createProxyWithNonce.assert_called_with(
        _singleton="0xSingleton", initializer=b"initializer", saltNonce=0
    )


def test_deploy_safe_v1_4_1(factory, mock_proxy_factory, mock_safe_singleton):
    mock_safe_singleton.encodeABI.return_value = b"initializer"
    chain_specific_func = mock_proxy_factory.functions.createChainSpecificProxyWithNonce
    chain_specific_func.return_value.call.return_value = "0xPredictedSafe"

    config = SafeAccountConfig(owners=["0xOwner1"], threshold=1)
    safe = factory.deploy_safe_v1_4_1(config)

    assert safe.get_address() == "0xPredictedSafe"
    mock_proxy_factory.functions.createChainSpecificProxyWithNonce.return_value.transact.assert_called_with(
        {"from": "0xSigner"}
    )
    mock_proxy_factory.functions.createChainSpecificProxyWithNonce.assert_called_with(
        _singleton="0xSingleton", initializer=b"initializer", saltNonce=0
    )
