"""CQL Interval type."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Optional, TypeVar

from .cql_type import CqlType

T = TypeVar("T")


@dataclass
class Interval(CqlType):
    """Represents an interval with low and high boundaries.

    An interval defines a range between two points with open or closed boundaries.
    """

    low: Any
    low_closed: bool
    high: Any
    high_closed: bool
    context: Optional[Any] = None

    def __post_init__(self):
        """Validate the interval after initialization."""
        # Determine point type
        point_type = None
        if self.low is not None:
            point_type = type(self.low)
        elif self.high is not None:
            point_type = type(self.high)

        if point_type is None:
            raise ValueError("Low or high boundary of an interval must be present.")

        self.point_type = point_type

        # Check that both boundaries are the same type
        if self.high is not None and type(self.high) != point_type:
            raise ValueError("Low and high boundary values of an interval must be of the same type.")

        # Validate ordering for Java dates
        if isinstance(self.low, date) and isinstance(self.high, date):
            if self.low > self.high:
                raise ValueError(
                    "Invalid Interval - the ending boundary must be greater than or equal to the starting boundary."
                )
        elif self.low is not None and self.high is not None:
            # Use comparison operators if available
            try:
                if self.low > self.high:
                    raise ValueError(
                        "Invalid Interval - the ending boundary must be greater than or equal to the starting boundary."
                    )
            except TypeError:
                # If comparison fails, skip validation
                pass

    def get_context(self) -> Optional[Any]:
        """Get the execution context."""
        return self.context

    def get_point_type(self) -> type:
        """Get the point type of this interval."""
        return self.point_type

    def is_uncertain(self) -> bool:
        """Check if this interval is uncertain."""
        return getattr(self, "_uncertain", False)

    def set_uncertain(self, uncertain: bool) -> "Interval":
        """Set whether this interval is uncertain.

        Args:
            uncertain: Whether the interval is uncertain

        Returns:
            Self for method chaining
        """
        self._uncertain = uncertain
        return self

    def get_start(self) -> Any:
        """Get the starting point of the interval.

        If the low boundary is open, returns the successor of the low value.
        If closed and low is not None, returns the low value.
        Otherwise returns the minimum value of the point type.
        """
        if not self.low_closed:
            # Return successor of low
            if self.low is None:
                return None
            if hasattr(self.low, "get_next_precision"):
                return self.low  # Placeholder for successor
            return self.low
        else:
            if self.low is None:
                # Return minimum value of point type
                return self._get_min_value()
            return self.low

    def get_end(self) -> Any:
        """Get the ending point of the interval.

        If the high boundary is open, returns the predecessor of the high value.
        If closed and high is not None, returns the high value.
        Otherwise returns the maximum value of the point type.
        """
        if not self.high_closed:
            # Return predecessor of high
            if self.high is None:
                return None
            if hasattr(self.high, "get_next_precision"):
                return self.high  # Placeholder for predecessor
            return self.high
        else:
            if self.high is None:
                # Return maximum value of point type
                return self._get_max_value()
            return self.high

    @staticmethod
    def get_size(start: Any, end: Any) -> Any:
        """Get the size/width of an interval.

        Args:
            start: The start value
            end: The end value

        Returns:
            The size, or None if either value is None
        """
        if start is None or end is None:
            return None

        if isinstance(start, (int, float, Decimal)):
            return end - start

        raise TypeError(
            f"Cannot perform width operator with argument of type '{type(start).__name__}'."
        )

    def _get_min_value(self) -> Any:
        """Get the minimum value for the point type."""
        if self.point_type in (int, float, Decimal):
            return 0 if self.point_type == int else 0.0
        return None

    def _get_max_value(self) -> Any:
        """Get the maximum value for the point type."""
        if self.point_type == int:
            return 2147483647  # Integer.MAX_VALUE
        elif self.point_type == float:
            return float("inf")
        elif self.point_type == Decimal:
            return Decimal("9999999999999999999999999999.99999999")
        return None

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if start and end are equivalent
        """
        if not isinstance(other, Interval):
            return False

        start_equiv = self._values_equivalent(self.get_start(), other.get_start())
        end_equiv = self._values_equivalent(self.get_end(), other.get_end())

        return start_equiv and end_equiv

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if equal, False if not, None if uncertain
        """
        if isinstance(other, Interval):
            if self.is_uncertain():
                if self.intersect(other) is not None:
                    return None

            start_equal = self._values_equal(self.get_start(), other.get_start())
            end_equal = self._values_equal(self.get_end(), other.get_end())

            if start_equal is None or end_equal is None:
                return None

            return start_equal and end_equal

        elif isinstance(other, int):
            # Compare with single value interval
            return self.equal(Interval(other, True, other, True, self.context))

        raise TypeError(
            f"Cannot perform equal operation on types: '{type(self).__name__}' and '{type(other).__name__}'"
        )

    @staticmethod
    def _values_equivalent(left: Any, right: Any) -> bool:
        """Check if two values are equivalent."""
        if left is None and right is None:
            return True
        if left is None or right is None:
            return False
        if hasattr(left, "equivalent"):
            return left.equivalent(right)
        return left == right

    @staticmethod
    def _values_equal(left: Any, right: Any) -> Optional[bool]:
        """Check if two values are equal."""
        if left is None and right is None:
            return True
        if left is None or right is None:
            return None
        if hasattr(left, "equal"):
            return left.equal(right)
        return left == right

    def intersect(self, other: "Interval") -> Optional["Interval"]:
        """Get the intersection of two intervals.

        Args:
            other: The other interval

        Returns:
            The intersection, or None if no overlap
        """
        # Placeholder for intersection logic
        return None

    def __lt__(self, other: "Interval") -> bool:
        """Compare for less than."""
        cql_list_cmp = CqlList()
        return cql_list_cmp.compare_to(self.get_start(), other.get_start()) < 0

    def __le__(self, other: "Interval") -> bool:
        """Compare for less than or equal."""
        cql_list_cmp = CqlList()
        start_cmp = cql_list_cmp.compare_to(self.get_start(), other.get_start())
        return start_cmp < 0 or (start_cmp == 0 and cql_list_cmp.compare_to(self.get_end(), other.get_end()) <= 0)

    def __gt__(self, other: "Interval") -> bool:
        """Compare for greater than."""
        cql_list_cmp = CqlList()
        return cql_list_cmp.compare_to(self.get_start(), other.get_start()) > 0

    def __ge__(self, other: "Interval") -> bool:
        """Compare for greater than or equal."""
        cql_list_cmp = CqlList()
        start_cmp = cql_list_cmp.compare_to(self.get_start(), other.get_start())
        return start_cmp > 0 or (start_cmp == 0 and cql_list_cmp.compare_to(self.get_end(), other.get_end()) >= 0)

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Interval):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash(
            (
                31 * (1 if self.low_closed else 0),
                47 * (1 if self.high_closed else 0),
                13 * (hash(self.low) if self.low is not None else 0),
                89 * (hash(self.high) if self.high is not None else 0),
            )
        )

    def __str__(self) -> str:
        """Get string representation."""
        low_bracket = "[" if self.low_closed else "("
        high_bracket = "]" if self.high_closed else ")"
        low_str = str(self.low) if self.low is not None else "null"
        high_str = str(self.high) if self.high is not None else "null"
        return f"Interval{low_bracket}{low_str}, {high_str}{high_bracket}"


# Import here to avoid circular imports
from .cql_list import CqlList
