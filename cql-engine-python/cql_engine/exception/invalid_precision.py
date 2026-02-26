"""
Invalid Precision Exception

Exception thrown when a precision value is invalid.
"""

from .cql_exception import CqlException


class InvalidPrecision(CqlException):
    """Exception thrown when an invalid precision is encountered."""

    def __init__(self, message: str) -> None:
        """
        Initialize an InvalidPrecision exception.

        Args:
            message: The exception message describing the invalid precision
        """
        super().__init__(message)
