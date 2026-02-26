"""
Invalid Cast Exception

Exception thrown when a type cast operation is invalid.
"""

from .cql_exception import CqlException


class InvalidCast(CqlException):
    """Exception thrown when an invalid type cast is attempted."""

    def __init__(self, message: str) -> None:
        """
        Initialize an InvalidCast exception.

        Args:
            message: The exception message describing the invalid cast
        """
        super().__init__(message)
