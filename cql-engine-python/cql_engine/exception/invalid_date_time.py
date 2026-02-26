"""
Invalid DateTime Exception

Exception thrown when a datetime value is invalid.
"""

from typing import Optional

from .cql_exception import CqlException


class InvalidDateTime(CqlException):
    """Exception thrown when an invalid datetime is encountered."""

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        """
        Initialize an InvalidDateTime exception.

        Args:
            message: The exception message describing the invalid datetime
            cause: The underlying exception (optional)
        """
        super().__init__(message, cause)
