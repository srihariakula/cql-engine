"""
Variable class for CQL engine execution.

Represents a variable in the execution context.
"""

from typing import Optional


class Variable:
    """
    Represents a variable in the CQL execution context.

    Variables are used to track identifiers and their values during expression evaluation.
    Supports both single values and list values.
    """

    def __init__(self):
        """Initialize an empty variable."""
        self.name: Optional[str] = None
        self.value: Optional[object] = None
        self.is_list: bool = False

    def set_is_list(self, is_list: bool) -> None:
        """
        Set whether this variable represents a list.

        Args:
            is_list: True if this variable is a list, False otherwise
        """
        self.is_list = is_list

    def is_list_var(self) -> bool:
        """
        Check if this variable represents a list.

        Returns:
            True if this variable is a list, False otherwise
        """
        return self.is_list

    def get_name(self) -> Optional[str]:
        """
        Get the variable name.

        Returns:
            The variable name
        """
        return self.name

    def set_name(self, name: str) -> None:
        """
        Set the variable name.

        Args:
            name: The variable name
        """
        self.name = name

    def with_name(self, name: str) -> 'Variable':
        """
        Set the variable name and return self for method chaining.

        Args:
            name: The variable name

        Returns:
            Self for method chaining
        """
        self.set_name(name)
        return self

    def get_value(self) -> Optional[object]:
        """
        Get the variable value.

        Returns:
            The variable value
        """
        return self.value

    def set_value(self, value: object) -> None:
        """
        Set the variable value.

        Args:
            value: The value to set
        """
        self.value = value

    def with_value(self, value: object) -> 'Variable':
        """
        Set the variable value and return self for method chaining.

        Args:
            value: The value to set

        Returns:
            Self for method chaining
        """
        self.set_value(value)
        return self
