"""CQL Quantity type."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from .cql_type import CqlType


@dataclass
class Quantity(CqlType):
    """Represents a quantity with a numeric value and unit.

    Quantities are used for measurements and include both a value and unit.
    """

    value: Decimal = field(default_factory=lambda: Decimal("0.0"))
    unit: str = field(default="1")

    DEFAULT_UNIT = "1"

    def __post_init__(self):
        """Ensure value is a Decimal."""
        if not isinstance(self.value, Decimal):
            self.value = Decimal(str(self.value))

    def with_value(self, value: Decimal | int | float | str) -> "Quantity":
        """Set the value.

        Args:
            value: The new value

        Returns:
            Self for method chaining
        """
        if not isinstance(value, Decimal):
            self.value = Decimal(str(value))
        else:
            self.value = value
        return self

    def with_unit(self, unit: str) -> "Quantity":
        """Set the unit.

        Args:
            unit: The new unit

        Returns:
            Self for method chaining
        """
        self.unit = unit
        return self

    def with_default_unit(self) -> "Quantity":
        """Set unit to the default.

        Returns:
            Self for method chaining
        """
        self.unit = self.DEFAULT_UNIT
        return self

    @staticmethod
    def is_default_unit(unit: Optional[str]) -> bool:
        """Check if a unit is the default unit.

        Args:
            unit: The unit to check

        Returns:
            True if unit is None, empty, or the default unit
        """
        return unit is None or unit == "" or unit == Quantity.DEFAULT_UNIT

    @staticmethod
    def units_equal(left_unit: str, right_unit: str) -> bool:
        """Check if two units are equal.

        Args:
            left_unit: First unit
            right_unit: Second unit

        Returns:
            True if units are equal
        """
        if Quantity.is_default_unit(left_unit) and Quantity.is_default_unit(right_unit):
            return True

        if Quantity.is_default_unit(left_unit):
            return False

        unit_map = {
            "year": {"year", "years"},
            "years": {"year", "years"},
            "month": {"month", "months"},
            "months": {"month", "months"},
            "week": {"week", "weeks", "wk"},
            "weeks": {"week", "weeks", "wk"},
            "wk": {"week", "weeks", "wk"},
            "day": {"day", "days", "d"},
            "days": {"day", "days", "d"},
            "d": {"day", "days", "d"},
            "hour": {"hour", "hours", "h"},
            "hours": {"hour", "hours", "h"},
            "h": {"hour", "hours", "h"},
            "minute": {"minute", "minutes", "min"},
            "minutes": {"minute", "minutes", "min"},
            "min": {"minute", "minutes", "min"},
            "second": {"second", "seconds", "s"},
            "seconds": {"second", "seconds", "s"},
            "s": {"second", "seconds", "s"},
            "millisecond": {"millisecond", "milliseconds", "ms"},
            "milliseconds": {"millisecond", "milliseconds", "ms"},
            "ms": {"millisecond", "milliseconds", "ms"},
        }

        return right_unit in unit_map.get(left_unit, {left_unit})

    @staticmethod
    def units_equivalent(left_unit: str, right_unit: str) -> bool:
        """Check if two units are equivalent.

        Equivalence is similar to equality but also includes alternate forms.

        Args:
            left_unit: First unit
            right_unit: Second unit

        Returns:
            True if units are equivalent
        """
        if Quantity.is_default_unit(left_unit) and Quantity.is_default_unit(right_unit):
            return True

        if Quantity.is_default_unit(left_unit):
            return False

        unit_map = {
            "year": {"year", "years", "a"},
            "years": {"year", "years", "a"},
            "a": {"year", "years", "a"},
            "month": {"month", "months", "mo"},
            "months": {"month", "months", "mo"},
            "mo": {"month", "months", "mo"},
            "week": {"week", "weeks", "wk"},
            "weeks": {"week", "weeks", "wk"},
            "wk": {"week", "weeks", "wk"},
            "day": {"day", "days", "d"},
            "days": {"day", "days", "d"},
            "d": {"day", "days", "d"},
            "hour": {"hour", "hours", "h"},
            "hours": {"hour", "hours", "h"},
            "h": {"hour", "hours", "h"},
            "minute": {"minute", "minutes", "min"},
            "minutes": {"minute", "minutes", "min"},
            "min": {"minute", "minutes", "min"},
            "second": {"second", "seconds", "s"},
            "seconds": {"second", "seconds", "s"},
            "s": {"second", "seconds", "s"},
            "millisecond": {"millisecond", "milliseconds", "ms"},
            "milliseconds": {"millisecond", "milliseconds", "ms"},
            "ms": {"millisecond", "milliseconds", "ms"},
        }

        return right_unit in unit_map.get(left_unit, {left_unit})

    def __lt__(self, other: "Quantity") -> bool:
        """Compare for less than."""
        if self.units_equal(self.unit, other.unit):
            return self.value < other.value
        raise TypeError("Cannot compare quantities with different units")

    def __le__(self, other: "Quantity") -> bool:
        """Compare for less than or equal."""
        if self.units_equal(self.unit, other.unit):
            return self.value <= other.value
        raise TypeError("Cannot compare quantities with different units")

    def __gt__(self, other: "Quantity") -> bool:
        """Compare for greater than."""
        if self.units_equal(self.unit, other.unit):
            return self.value > other.value
        raise TypeError("Cannot compare quantities with different units")

    def __ge__(self, other: "Quantity") -> bool:
        """Compare for greater than or equal."""
        if self.units_equal(self.unit, other.unit):
            return self.value >= other.value
        raise TypeError("Cannot compare quantities with different units")

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Quantity):
            return False
        return self.equal(other) or False

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((self.value, self.unit))

    def comparable_to(self, other: "Quantity") -> Optional[int]:
        """Compare if units are equal, return None if they differ.

        Args:
            other: The quantity to compare with

        Returns:
            -1 if less, 0 if equal, 1 if greater, None if units don't match
        """
        if self.units_equal(self.unit, other.unit):
            return -1 if self.value < other.value else (0 if self.value == other.value else 1)
        return None

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if equivalent units and equal values
        """
        if not isinstance(other, Quantity):
            return False
        return self.units_equivalent(self.unit, other.unit) and self.value == other.value

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if equal units and values, False if not, None if uncertain
        """
        if not isinstance(other, Quantity):
            return False
        if self.units_equal(self.unit, other.unit):
            return self.value == other.value
        return None

    def __str__(self) -> str:
        """Get string representation."""
        return f"{self.value} '{self.unit}'"
