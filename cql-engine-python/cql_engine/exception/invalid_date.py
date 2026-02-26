"""
Invalid Date Exception

Exception thrown when a date value is invalid.
"""

from .cql_exception import CqlException


class InvalidDate(CqlException):
    """Exception thrown when an invalid date is encountered."""

    def __init__(self, message: str) -> None:
        """
        Initialize an InvalidDate exception.

        Args:
            message: The exception message describing the invalid date
        """
        super().__init__(message)
