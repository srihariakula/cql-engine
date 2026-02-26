"""
Invalid Conversion Exception

Exception thrown when a type conversion operation is invalid.
"""

from typing import Any

from .cql_exception import CqlException


class InvalidConversion(CqlException):
    """Exception thrown when an invalid type conversion is attempted."""

    def __init__(self, message_or_from: Any, to: Any = None) -> None:
        """
        Initialize an InvalidConversion exception.

        Can be called in two ways:
        1. InvalidConversion(message: str) - with just a message
        2. InvalidConversion(from_value, to_value) - with types to convert between

        Args:
            message_or_from: Either the error message or the source object/type
            to: The target object/type (when using two-argument form)
        """
        if to is not None:
            # Two-argument form: InvalidConversion(from, to)
            from_type = type(message_or_from).__name__
            to_type = type(to).__name__
            message = f"Cannot Convert a value of type {from_type} as {to_type}."
        else:
            # Single-argument form: InvalidConversion(message)
            message = message_or_from

        super().__init__(message)
