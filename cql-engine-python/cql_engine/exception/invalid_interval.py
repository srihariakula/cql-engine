"""
Invalid Interval Exception

Exception thrown when an interval value is invalid.
"""

from .cql_exception import CqlException


class InvalidInterval(CqlException):
    """Exception thrown when an invalid interval is encountered."""

    def __init__(self, message: str) -> None:
        """
        Initialize an InvalidInterval exception.

        Args:
            message: The exception message describing the invalid interval
        """
        super().__init__(message)
