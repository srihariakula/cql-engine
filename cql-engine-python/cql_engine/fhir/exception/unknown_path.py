"""Unknown path exception."""


class UnknownPath(Exception):
    """Exception raised when a path cannot be resolved."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Description of the unknown path
        """
        super().__init__(message)
