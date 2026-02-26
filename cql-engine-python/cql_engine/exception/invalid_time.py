"""
Invalid Time Exception

Exception thrown when a time value is invalid.
"""

from .cql_exception import CqlException


class InvalidTime(CqlException):
    """Exception thrown when an invalid time is encountered."""

    def __init__(self, message: str) -> None:
        """
        Initialize an InvalidTime exception.

        Args:
            message: The exception message describing the invalid time
        """
        super().__init__(message)
