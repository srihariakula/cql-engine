"""
Type Overflow Exception

Exception thrown when a numeric value overflows its type.
"""

from .cql_exception import CqlException


class TypeOverflow(CqlException):
    """Exception thrown when a numeric value overflows its type."""

    def __init__(self, message: str) -> None:
        """
        Initialize a TypeOverflow exception.

        Args:
            message: The exception message describing the overflow condition
        """
        super().__init__(message)
