# Safe Kit v0.0.14 Release Summary

## Release Date
January 23, 2026

## Overview
Version 0.0.14 introduces significant developer experience improvements with fluent transaction building APIs, enhanced error handling, performance optimizations through caching, and comprehensive transaction status utilities.

## New Features

### 1. Transaction Builder Pattern
A fluent API for creating complex transactions with method chaining.

**Usage:**
```python
tx = safe.tx() \
    .send_eth("0x123...", 1000000000000000000) \
    .send_erc20("0xToken...", "0x456...", 100) \
    .send_erc721("0xNFT...", "0x789...", token_id=42) \
    .build()
```

**Benefits:**
- More readable and maintainable code
- Automatic batch transaction creation for multiple operations
- Type-safe method chaining

### 2. Batch Transaction Helper
Simplified MultiSend transaction creation without manual encoding.

**Usage:**
```python
tx1 = SafeTransactionData(to="0x123...", value=1000, data="0x")
tx2 = SafeTransactionData(to="0x456...", value=2000, data="0x")
batch_tx = safe.create_batch_transaction([tx1, tx2])
```

**Benefits:**
- No need to manually import and use MultiSend class
- Automatic encoding of multiple transactions
- Uses canonical MultiSend contract address by default

### 3. Enhanced Error Handling
Specific exception classes for common error scenarios.

**New Exception Classes:**
- `InsufficientSignaturesError` - Transaction lacks required signatures
- `InvalidThresholdError` - Invalid threshold value specified
- `OwnerNotFoundError` - Owner address not found in Safe
- `OwnerAlreadyExistsError` - Attempting to add existing owner
- `ModuleNotEnabledError` - Module is not enabled
- `InvalidAddressError` - Invalid Ethereum address format
- `TransactionNotFoundError` - Transaction not found

**Usage:**
```python
try:
    safe.execute_transaction(signed_tx)
except InsufficientSignaturesError as e:
    print(f"Need {e.required - e.provided} more signatures")
```

### 4. Transaction Status Utilities
Methods to check transaction status before execution.

**New Methods:**
- `get_signature_count(safe_tx)` - Get number of signatures
- `has_enough_signatures(safe_tx)` - Check if transaction is ready
- `get_missing_signatures(safe_tx)` - Get number of missing signatures
- `get_signers(safe_tx)` - Get list of addresses that signed

**Usage:**
```python
if not safe.has_enough_signatures(safe_tx):
    missing = safe.get_missing_signatures(safe_tx)
    print(f"Need {missing} more signatures")
```

### 5. Safe Info Caching
Optional caching mechanism to reduce RPC calls for frequently accessed properties.

**Usage:**
```python
safe = Safe(
    eth_adapter=adapter,
    safe_address="0x...",
    enable_cache=True,
    cache_ttl=60  # Cache for 60 seconds
)

# Subsequent calls within TTL use cache
owners = safe.get_owners()  # RPC call
threshold = safe.get_threshold()  # RPC call
owners2 = safe.get_owners()  # Uses cache, no RPC call

# Manual cache management
safe.clear_cache()  # Clear all cached data
safe.invalidate_cache("owners")  # Invalidate specific entry
```

**Benefits:**
- Reduced RPC calls for frequently accessed data
- Configurable TTL for cache expiration
- Manual cache invalidation when needed
- Thread-safe implementation

## Testing
- Added 20 new test cases covering all new features
- All 92 tests passing
- Test coverage maintained at >85%
- Type checking passes with mypy
- Linting passes with ruff

## Documentation
- Updated user guide with examples for all new features
- Created comprehensive example file: `examples/v0_0_14_features.py`
- Updated CHANGELOG.md with detailed feature descriptions
- Updated roadmap.md to reflect v0.0.14 release

## Files Changed
- `safe_kit/safe.py` - Added new methods and caching support
- `safe_kit/builder.py` - New TransactionBuilder class
- `safe_kit/cache.py` - New SafeCache implementation
- `safe_kit/errors.py` - Added specific exception classes
- `safe_kit/__init__.py` - Exported new classes and exceptions
- `pyproject.toml` - Version bump to 0.0.14
- `CHANGELOG.md` - Documented all changes
- `docs/roadmap.md` - Updated roadmap
- `docs/user_guide.md` - Added documentation for new features
- `examples/v0_0_14_features.py` - New comprehensive example
- `tests/test_new_features.py` - New test suite

## Breaking Changes
None. This release is fully backward compatible with v0.0.13.

## Next Steps
After reviewing this release, you can:
1. Tag the release: `git tag v0.0.14`
2. Push to GitHub: `git push && git push --tags`
3. Publish to PyPI: `poetry publish --build`

## Migration Guide
No migration required. All existing code will continue to work. To use new features:

### Enable Caching
```python
# Old
safe = Safe(eth_adapter=adapter, safe_address="0x...")

# New (with caching)
safe = Safe(
    eth_adapter=adapter,
    safe_address="0x...",
    enable_cache=True,
    cache_ttl=60
)
```

### Use Transaction Builder
```python
# Old
tx_data = SafeTransactionData(to="0x...", value=1000, data="0x")
safe_tx = safe.create_transaction(tx_data)

# New (fluent API)
safe_tx = safe.tx().send_eth("0x...", 1000).build()
```

### Use Batch Helper
```python
# Old
from safe_kit.multisend import MultiSend
encoded = MultiSend.encode_transactions([tx1, tx2])
batch_data = SafeTransactionData(
    to=multisend_address,
    value=0,
    data="0x8d80ff0a" + encoded.hex(),
    operation=1
)
batch_tx = safe.create_transaction(batch_data)

# New (simplified)
batch_tx = safe.create_batch_transaction([tx1, tx2])
```

## Credits
Developed by smallyu
