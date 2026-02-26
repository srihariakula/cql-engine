"""
Type Underflow Exception

Exception thrown when a numeric value underflows its type.
"""

from .cql_exception import CqlException


class TypeUnderflow(CqlException):
    """Exception thrown when a numeric value underflows its type."""

    def __init__(self, message: str) -> None:
        """
        Initialize a TypeUnderflow exception.

        Args:
            message: The exception message describing the underflow condition
        """
        super().__init__(message)
