"""CQL Ratio type."""

from dataclasses import dataclass, field
from typing import Optional

from .cql_type import CqlType
from .quantity import Quantity


@dataclass
class Ratio(CqlType):
    """Represents a ratio of two quantities.

    A ratio consists of a numerator and denominator quantity.
    """

    numerator: Optional[Quantity] = None
    denominator: Optional[Quantity] = None

    def set_numerator(self, numerator: Quantity) -> "Ratio":
        """Set the numerator.

        Args:
            numerator: The new numerator

        Returns:
            Self for method chaining
        """
        self.numerator = numerator
        return self

    def set_denominator(self, denominator: Quantity) -> "Ratio":
        """Set the denominator.

        Args:
            denominator: The new denominator

        Returns:
            Self for method chaining
        """
        self.denominator = denominator
        return self

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if both numerator and denominator are equivalent
        """
        if not isinstance(other, Ratio):
            return False
        numerator_equiv = (
            self.numerator.equivalent(other.numerator)
            if self.numerator and other.numerator
            else self.numerator is None and other.numerator is None
        )
        denominator_equiv = (
            self.denominator.equivalent(other.denominator)
            if self.denominator and other.denominator
            else self.denominator is None and other.denominator is None
        )
        return numerator_equiv and denominator_equiv

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if equal, False if not, None if uncertain
        """
        if not isinstance(other, Ratio):
            return False
        numerator_equal = (
            self.numerator.equal(other.numerator)
            if self.numerator and other.numerator
            else self.numerator is None and other.numerator is None
        )
        denominator_equal = (
            self.denominator.equal(other.denominator)
            if self.denominator and other.denominator
            else self.denominator is None and other.denominator is None
        )

        if numerator_equal is None or denominator_equal is None:
            return None
        return numerator_equal and denominator_equal

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Ratio):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((self.numerator, self.denominator))

    def __str__(self) -> str:
        """Get string representation."""
        numerator_str = str(self.numerator) if self.numerator else "None"
        denominator_str = str(self.denominator) if self.denominator else "None"
        return f"{numerator_str}:{denominator_str}"
