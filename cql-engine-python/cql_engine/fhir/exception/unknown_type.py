"""Unknown type exception."""


class UnknownType(Exception):
    """Exception raised when a type cannot be resolved."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Description of the unknown type
        """
        super().__init__(message)
