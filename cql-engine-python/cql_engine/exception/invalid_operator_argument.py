"""
Invalid Operator Argument Exception

Exception thrown when an operator receives invalid arguments.
"""

from typing import Optional

from .cql_exception import CqlException


class InvalidOperatorArgument(CqlException):
    """Exception thrown when an operator receives invalid arguments."""

    def __init__(self, expected_or_message: str, found: Optional[str] = None) -> None:
        """
        Initialize an InvalidOperatorArgument exception.

        Can be called in two ways:
        1. InvalidOperatorArgument(message: str) - with just a message
        2. InvalidOperatorArgument(expected: str, found: str) - with expected vs found

        Args:
            expected_or_message: Either the error message or expected argument type
            found: The actual argument type (when using two-argument form)
        """
        if found is not None:
            # Two-argument form: InvalidOperatorArgument(expected, found)
            message = f"Expected {expected_or_message}, Found {found}"
        else:
            # Single-argument form: InvalidOperatorArgument(message)
            message = expected_or_message

        super().__init__(message)
