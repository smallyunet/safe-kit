class SafeKitError(Exception):
    """Base exception for safe-kit"""

    pass


class SafeTransactionError(SafeKitError):
    """Exception raised when a Safe transaction fails"""

    def __init__(self, message: str, error_code: str | None = None):
        self.error_code = error_code
        super().__init__(f"{error_code}: {message}" if error_code else message)


class SafeServiceError(SafeKitError):
    """Exception raised when the Safe Transaction Service returns an error"""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(f"Status {status_code}: {message}" if status_code else message)


class InsufficientSignaturesError(SafeKitError):
    """Exception raised when a transaction doesn't have enough signatures"""

    def __init__(self, required: int, provided: int):
        self.required = required
        self.provided = provided
        super().__init__(
            f"Insufficient signatures: required {required}, provided {provided}"
        )


class InvalidThresholdError(SafeKitError):
    """Exception raised when an invalid threshold is specified"""

    def __init__(self, threshold: int, owner_count: int):
        self.threshold = threshold
        self.owner_count = owner_count
        super().__init__(
            f"Invalid threshold: {threshold} (must be between 1 and {owner_count})"
        )


class OwnerNotFoundError(SafeKitError):
    """Exception raised when an owner is not found in the Safe"""

    def __init__(self, owner_address: str):
        self.owner_address = owner_address
        super().__init__(f"Owner not found: {owner_address}")


class OwnerAlreadyExistsError(SafeKitError):
    """Exception raised when trying to add an owner that already exists"""

    def __init__(self, owner_address: str):
        self.owner_address = owner_address
        super().__init__(f"Owner already exists: {owner_address}")


class ModuleNotEnabledError(SafeKitError):
    """Exception raised when a module is not enabled"""

    def __init__(self, module_address: str):
        self.module_address = module_address
        super().__init__(f"Module not enabled: {module_address}")


class InvalidAddressError(SafeKitError):
    """Exception raised when an invalid Ethereum address is provided"""

    def __init__(self, address: str):
        self.address = address
        super().__init__(f"Invalid Ethereum address: {address}")


class TransactionNotFoundError(SafeKitError):
    """Exception raised when a transaction is not found"""

    def __init__(self, tx_hash: str):
        self.tx_hash = tx_hash
        super().__init__(f"Transaction not found: {tx_hash}")


SAFE_ERRORS = {
    "GS000": "Could not finish initialization",
    "GS001": "Threshold needs to be defined",
    "GS010": "Not enough gas to execute Safe transaction",
    "GS011": "Could not pay gas costs with ether",
    "GS012": "Could not pay gas costs with token",
    "GS013": "Safe transaction failed when gasPrice and safeTxGas were 0",
    "GS020": "Signatures data too short",
    "GS021": "Invalid signature provided",
    "GS022": "Invalid signature provided (duplicate)",
    "GS023": "Invalid signature provided (not owner)",
    "GS024": "Invalid signature provided (not sorted)",
    "GS025": "Invalid signature provided (v is 0)",
    "GS026": "Invalid signature provided (v > 30)",
    "GS030": "Only owners can approve a hash",
    "GS031": "Hash has already been approved",
    "GS100": "Modules have already been initialized",
    "GS130": "New owner cannot be the null address",
}


def handle_contract_error(e: Exception) -> Exception:
    """
    Parses a web3 exception and returns a more readable SafeKitError if possible.
    """
    error_str = str(e)

    # Check for Safe error codes in the exception message
    for code, message in SAFE_ERRORS.items():
        if code in error_str:
            return SafeTransactionError(message, error_code=code)

    # If no specific Safe error is found, return the original exception
    # or wrap it in a generic SafeKitError
    return e
