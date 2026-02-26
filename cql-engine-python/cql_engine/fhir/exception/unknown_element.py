"""Unknown element exception."""


class UnknownElement(Exception):
    """Exception raised when an element cannot be found."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Description of the unknown element
        """
        super().__init__(message)
