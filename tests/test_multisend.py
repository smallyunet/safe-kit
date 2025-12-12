from safe_kit.multisend import MultiSend
from safe_kit.types import SafeTransactionData


def test_encode_transactions():
    tx1 = SafeTransactionData(
        to="0x1234567890123456789012345678901234567890",
        value=100,
        data="0x",
        operation=0
    )
    tx2 = SafeTransactionData(
        to="0x0987654321098765432109876543210987654321",
        value=0,
        data="0xabcdef",
        operation=1
    )
    
    encoded = MultiSend.encode_transactions([tx1, tx2])
    
    # Verify length and content roughly
    # Each tx: 1 (op) + 20 (to) + 32 (value) + 32 (data_len) + data_bytes
    
    # Tx1: 1 + 20 + 32 + 32 + 0 = 85 bytes
    # Tx2: 1 + 20 + 32 + 32 + 3 (0xabcdef) = 88 bytes
    # Total: 173 bytes
    
    assert len(encoded) == 173
    
    # Check first byte (operation of tx1)
    assert encoded[0] == 0
    
    # Check operation of tx2 (index 85)
    assert encoded[85] == 1
