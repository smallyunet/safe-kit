from typing import TYPE_CHECKING

from safe_kit.types import SafeTransaction, SafeTransactionData

if TYPE_CHECKING:
    from safe_kit.safe import Safe


class TransactionBuilder:
    """
    A fluent API builder for creating Safe transactions.

    This class provides a chainable interface for building complex transactions
    with multiple operations. It's particularly useful for creating batch transactions
    in a more readable and maintainable way.

    Example:
        tx = safe.tx() \\
            .send_eth("0x123...", 1000000000000000000) \\
            .send_erc20("0xToken...", "0x456...", 100) \\
            .build()
    """

    def __init__(self, safe: "Safe"):
        self.safe = safe
        self.transactions: list[SafeTransactionData] = []

    def send_eth(self, to: str, value: int) -> "TransactionBuilder":
        """
        Add an ETH transfer to the batch.

        Args:
            to: The recipient address
            value: The amount of ETH to send in wei

        Returns:
            Self for chaining
        """
        self.transactions.append(
            SafeTransactionData(
                to=to,
                value=value,
                data="0x",
                operation=0,
            )
        )
        return self

    def send_erc20(self, token: str, to: str, amount: int) -> "TransactionBuilder":
        """
        Add an ERC20 transfer to the batch.

        Args:
            token: The ERC20 token contract address
            to: The recipient address
            amount: The amount of tokens to send (in token's smallest unit)

        Returns:
            Self for chaining
        """
        # ERC20 transfer(address,uint256) function selector
        transfer_data = (
            "0xa9059cbb"
            + to.replace("0x", "").zfill(64)
            + hex(amount)[2:].zfill(64)
        )

        self.transactions.append(
            SafeTransactionData(
                to=token,
                value=0,
                data=transfer_data,
                operation=0,
            )
        )
        return self

    def send_erc721(
        self, token: str, to: str, token_id: int, from_address: str | None = None
    ) -> "TransactionBuilder":
        """
        Add an ERC721 (NFT) transfer to the batch.

        Args:
            token: The ERC721 token contract address
            to: The recipient address
            token_id: The token ID to transfer
            from_address: The current owner (defaults to Safe address)

        Returns:
            Self for chaining
        """
        if from_address is None:
            from_address = self.safe.get_address()

        # ERC721 transferFrom(address,address,uint256) function selector
        transfer_data = (
            "0x23b872dd"
            + from_address.replace("0x", "").zfill(64)
            + to.replace("0x", "").zfill(64)
            + hex(token_id)[2:].zfill(64)
        )

        self.transactions.append(
            SafeTransactionData(
                to=token,
                value=0,
                data=transfer_data,
                operation=0,
            )
        )
        return self

    def call(
        self,
        to: str,
        data: str,
        value: int = 0,
        operation: int = 0,
    ) -> "TransactionBuilder":
        """
        Add a custom contract call to the batch.

        Args:
            to: The contract address to call
            data: The encoded function call data
            value: The ETH value to send (default: 0)
            operation: The operation type (0=Call, 1=DelegateCall)

        Returns:
            Self for chaining
        """
        self.transactions.append(
            SafeTransactionData(
                to=to,
                value=value,
                data=data,
                operation=operation,
            )
        )
        return self

    def build(self) -> SafeTransaction:
        """
        Build the final Safe transaction.

        If multiple transactions were added, creates a batched transaction
        using MultiSend. If only one transaction was added, returns a
        simple transaction.

        Returns:
            A SafeTransaction ready to be signed and executed

        Raises:
            ValueError: If no transactions were added
        """
        if not self.transactions:
            raise ValueError("No transactions added to the builder")

        if len(self.transactions) == 1:
            return self.safe.create_transaction(self.transactions[0])
        else:
            return self.safe.create_batch_transaction(self.transactions)

    def clear(self) -> "TransactionBuilder":
        """
        Clear all transactions from the builder.

        Returns:
            Self for chaining
        """
        self.transactions = []
        return self
