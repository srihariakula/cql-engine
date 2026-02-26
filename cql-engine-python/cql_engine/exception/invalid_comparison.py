"""
Invalid Comparison Exception

Exception thrown when a comparison operation is invalid.
"""

from .cql_exception import CqlException


class InvalidComparison(CqlException):
    """Exception thrown when an invalid comparison is attempted."""

    def __init__(self, message: str) -> None:
        """
        Initialize an InvalidComparison exception.

        Args:
            message: The exception message describing the invalid comparison
        """
        super().__init__(message)
