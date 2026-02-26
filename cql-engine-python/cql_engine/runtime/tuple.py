"""CQL Tuple type."""

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Optional

from .cql_type import CqlType


@dataclass
class Tuple(CqlType):
    """Represents a tuple with named elements.

    A tuple is a collection of key-value pairs with ordered preservation.
    """

    elements: OrderedDict[str, Any] = field(default_factory=OrderedDict)
    context: Optional[Any] = None

    def get_element(self, key: str) -> Any:
        """Get an element by key.

        Args:
            key: The element key

        Returns:
            The element value, or None if not found
        """
        return self.elements.get(key)

    def set_elements(self, elements: OrderedDict[str, Any]) -> None:
        """Set the elements.

        Args:
            elements: The new elements
        """
        self.elements = elements

    def with_elements(self, elements: OrderedDict[str, Any]) -> "Tuple":
        """Set the elements.

        Args:
            elements: The new elements

        Returns:
            Self for method chaining
        """
        self.set_elements(elements)
        return self

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if all elements are equivalent
        """
        if not isinstance(other, Tuple):
            return False

        if len(self.elements) != len(other.elements):
            return False

        for key, value in other.elements.items():
            if key not in self.elements:
                return False

            # Simple equivalence check - if values are equal
            if self.elements[key] != value:
                # Try calling equivalent method if available
                if hasattr(self.elements[key], "equivalent"):
                    if not self.elements[key].equivalent(value):
                        return False
                else:
                    return False

        return True

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if equal, False if not, None if uncertain
        """
        if not isinstance(other, Tuple):
            return False

        if len(self.elements) != len(other.elements):
            return False

        for key, value in other.elements.items():
            if key not in self.elements:
                return False

            # Both are None
            if value is None and self.elements[key] is None:
                continue

            # Check equality
            if hasattr(value, "equal"):
                result = value.equal(self.elements[key])
            else:
                result = value == self.elements[key]

            if result is None:
                return None
            elif not result:
                return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Tuple):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash(tuple(self.elements.items()))

    def __str__(self) -> str:
        """Get string representation."""
        if not self.elements:
            return "Tuple { : }"

        lines = ["Tuple {"]
        for key, value in self.elements.items():
            value_str = str(value) if value is not None else "null"
            lines.append(f'\t"{key}": {value_str}')
        lines.append("}")
        return "\n".join(lines)
