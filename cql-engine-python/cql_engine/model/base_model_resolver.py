"""
Base model resolver implementation with common type casting logic.
"""

from typing import Optional
from cql_engine.model.model_resolver import ModelResolver


class InvalidCast(Exception):
    """Exception raised when a type cast cannot be performed."""
    pass


class BaseModelResolver(ModelResolver):
    """
    Abstract base implementation of ModelResolver providing default implementations
    for type checking and casting operations.
    """

    def is_instance(self, value: object, type_: type) -> Optional[bool]:
        """
        Check whether or not a specified value instance is of the specified type.

        Args:
            value: The value to check
            type_: The type to check against

        Returns:
            True if value is an instance of type_, False otherwise, None if value is None
        """
        if value is None:
            return None

        if isinstance(value, type_):
            return True

        return False

    def as_type(self, value: object, type_: type, is_strict: bool = False) -> object:
        """
        Cast the specified value to the specified type.

        Args:
            value: The value to cast
            type_: The type to cast to
            is_strict: If True, raise exception on invalid cast; if False, return None

        Returns:
            The value if it's already of the correct type, None otherwise

        Raises:
            InvalidCast: If is_strict is True and cast is not possible
        """
        if value is None:
            return None

        if isinstance(value, type_):
            return value

        if is_strict:
            raise InvalidCast(
                f"Cannot cast a value of type {type(value).__name__} as {type_.__name__}."
            )

        return None
