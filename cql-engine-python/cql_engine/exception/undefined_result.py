"""
Undefined Result Exception

Exception thrown when an operation results in an undefined value.
"""

from .cql_exception import CqlException


class UndefinedResult(CqlException):
    """Exception thrown when an operation results in an undefined value."""

    def __init__(self, message: str) -> None:
        """
        Initialize an UndefinedResult exception.

        Args:
            message: The exception message describing the undefined result
        """
        super().__init__(message)
