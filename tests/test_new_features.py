import time

import pytest

from safe_kit.builder import TransactionBuilder
from safe_kit.cache import SafeCache
from safe_kit.errors import (
    InsufficientSignaturesError,
    InvalidAddressError,
    InvalidThresholdError,
    ModuleNotEnabledError,
    OwnerAlreadyExistsError,
    OwnerNotFoundError,
    TransactionNotFoundError,
)
from safe_kit.types import SafeTransactionData


class TestCustomExceptions:
    """Test custom exception classes"""

    def test_insufficient_signatures_error(self):
        error = InsufficientSignaturesError(required=3, provided=1)
        assert error.required == 3
        assert error.provided == 1
        assert "required 3" in str(error)
        assert "provided 1" in str(error)

    def test_invalid_threshold_error(self):
        error = InvalidThresholdError(threshold=5, owner_count=3)
        assert error.threshold == 5
        assert error.owner_count == 3
        assert "5" in str(error)
        assert "between 1 and 3" in str(error)

    def test_owner_not_found_error(self):
        error = OwnerNotFoundError(owner_address="0x123")
        assert error.owner_address == "0x123"
        assert "0x123" in str(error)

    def test_owner_already_exists_error(self):
        error = OwnerAlreadyExistsError(owner_address="0x456")
        assert error.owner_address == "0x456"
        assert "0x456" in str(error)

    def test_module_not_enabled_error(self):
        error = ModuleNotEnabledError(module_address="0x789")
        assert error.module_address == "0x789"
        assert "0x789" in str(error)

    def test_invalid_address_error(self):
        error = InvalidAddressError(address="invalid")
        assert error.address == "invalid"
        assert "invalid" in str(error)

    def test_transaction_not_found_error(self):
        error = TransactionNotFoundError(tx_hash="0xabc")
        assert error.tx_hash == "0xabc"
        assert "0xabc" in str(error)


class TestSafeCache:
    """Test SafeCache functionality"""

    def test_cache_set_and_get(self):
        cache = SafeCache(ttl=60)
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

    def test_cache_expiration(self):
        cache = SafeCache(ttl=1)
        cache.set("test_key", "test_value")
        time.sleep(1.1)
        assert cache.get("test_key") is None

    def test_cache_invalidate(self):
        cache = SafeCache(ttl=60)
        cache.set("test_key", "test_value")
        cache.invalidate("test_key")
        assert cache.get("test_key") is None

    def test_cache_clear(self):
        cache = SafeCache(ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_get_nonexistent(self):
        cache = SafeCache(ttl=60)
        assert cache.get("nonexistent") is None


class TestTransactionBuilder:
    """Test TransactionBuilder functionality"""

    def test_builder_single_eth_transfer(self, mock_safe):
        builder = TransactionBuilder(mock_safe)
        addr = "0x1234567890123456789012345678901234567890"
        tx = builder.send_eth(addr, 1000).build()

        assert isinstance(tx.data, SafeTransactionData)
        assert tx.data.to == addr
        assert tx.data.value == 1000
        assert tx.data.data == "0x"

    def test_builder_erc20_transfer(self, mock_safe):
        builder = TransactionBuilder(mock_safe)
        tx = (
            builder.send_erc20(
                "0x1111111111111111111111111111111111111111",
                "0x2222222222222222222222222222222222222222",
                1000,
            ).build()
        )

        assert tx.data.to == "0x1111111111111111111111111111111111111111"
        assert tx.data.value == 0
        assert "a9059cbb" in tx.data.data  # transfer function selector

    def test_builder_erc721_transfer(self, mock_safe):
        builder = TransactionBuilder(mock_safe)
        tx = (
            builder.send_erc721(
                "0x1111111111111111111111111111111111111111",
                "0x2222222222222222222222222222222222222222",
                123,
            ).build()
        )

        assert tx.data.to == "0x1111111111111111111111111111111111111111"
        assert tx.data.value == 0
        assert "23b872dd" in tx.data.data  # transferFrom function selector

    def test_builder_custom_call(self, mock_safe):
        builder = TransactionBuilder(mock_safe)
        tx = (
            builder.call(
                "0x1111111111111111111111111111111111111111",
                "0x12345678",
                value=500,
                operation=1,
            ).build()
        )

        assert tx.data.to == "0x1111111111111111111111111111111111111111"
        assert tx.data.value == 500
        assert tx.data.data == "0x12345678"
        assert tx.data.operation == 1

    def test_builder_multiple_transactions(self, mock_safe):
        builder = TransactionBuilder(mock_safe)
        tx = (
            builder.send_eth("0x1111111111111111111111111111111111111111", 1000)
            .send_erc20(
                "0x2222222222222222222222222222222222222222",
                "0x3333333333333333333333333333333333333333",
                500,
            )
            .build()
        )

        # Should create a batch transaction
        assert tx.data.operation == 1  # DelegateCall for MultiSend

    def test_builder_clear(self, mock_safe):
        builder = TransactionBuilder(mock_safe)
        builder.send_eth("0x1111111111111111111111111111111111111111", 1000)
        builder.clear()
        assert len(builder.transactions) == 0

    def test_builder_empty_build_raises_error(self, mock_safe):
        builder = TransactionBuilder(mock_safe)
        with pytest.raises(ValueError, match="No transactions added"):
            builder.build()

    def test_builder_chaining(self, mock_safe):
        builder = TransactionBuilder(mock_safe)
        result = (
            builder.send_eth("0x1111111111111111111111111111111111111111", 1000)
            .send_eth("0x2222222222222222222222222222222222222222", 2000)
            .send_eth("0x3333333333333333333333333333333333333333", 3000)
        )
        assert result is builder  # Should return self for chaining
        assert len(builder.transactions) == 3


@pytest.fixture
def mock_safe():
    """Create a mock Safe instance for testing"""
    from unittest.mock import Mock

    from safe_kit.safe import Safe

    mock = Mock(spec=Safe)
    mock.get_address.return_value = "0x9999999999999999999999999999999999999999"
    mock.get_nonce.return_value = 0

    def create_tx(data):
        from safe_kit.types import SafeTransaction

        if data.nonce is None:
            data.nonce = 0
        return SafeTransaction(data=data)

    def create_batch_tx(transactions):
        from safe_kit.multisend import MultiSend
        from safe_kit.types import SafeTransaction

        encoded_data = MultiSend.encode_transactions(transactions)
        batch_data = SafeTransactionData(
            to="0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
            value=0,
            data="0x8d80ff0a" + encoded_data.hex(),
            operation=1,
            nonce=0,
        )
        return SafeTransaction(data=batch_data)

    mock.create_transaction.side_effect = create_tx
    mock.create_batch_transaction.side_effect = create_batch_tx

    return mock
