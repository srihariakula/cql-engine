"""CQL Date type."""

from datetime import date as py_date, datetime as py_datetime, timezone
from typing import Optional
from dateutil import parser as date_parser

from .base_temporal import BaseTemporal
from .precision import Precision
from .temporal_helper import TemporalHelper


class Date(BaseTemporal):
    """Represents a CQL Date value.

    Dates in CQL can have varying precision (year, month, or day).
    """

    __slots__ = ("_date",)

    def __init__(
        self,
        year_or_date: int | str | py_date,
        month: Optional[int] = None,
        day: Optional[int] = None,
        precision: Optional[Precision] = None,
    ):
        """Initialize a Date instance.

        Args:
            year_or_date: Either year as int, date string, or Python date object
            month: Month (if year_or_date is int)
            day: Day (if year_or_date is int)
            precision: The precision of this date

        Raises:
            ValueError: If year is out of bounds (1-9999)
        """
        super().__init__(precision)

        if isinstance(year_or_date, str):
            # Parse from string like "2021-05-15"
            self._date = self._parse_date_string(year_or_date)
            if precision is None:
                parts = year_or_date.split("-")
                self.precision = Precision.from_date_index(len(parts) - 1)
        elif isinstance(year_or_date, py_date):
            self._date = year_or_date
            if precision is None:
                self.precision = Precision.DAY
        elif isinstance(year_or_date, int):
            # Create from components
            month = month or 1
            day = day or 1
            self._date = py_date(year_or_date, month, day)
            if precision is None:
                self.precision = Precision.DAY if day else Precision.MONTH if month else Precision.YEAR

        # Validate year bounds
        if self._date.year < 1 or self._date.year > 9999:
            raise ValueError(
                f"The year: {self._date.year} falls outside the accepted bounds of 0001-9999."
            )

    @staticmethod
    def _parse_date_string(date_str: str) -> py_date:
        """Parse a date string.

        Args:
            date_str: Date string in ISO format

        Returns:
            Python date object

        Raises:
            ValueError: If the string cannot be parsed
        """
        # Auto-complete the date string first
        parts = date_str.split("-")
        precision = Precision.from_date_index(len(parts) - 1)
        date_str = TemporalHelper.auto_complete_date_string(date_str, precision)
        return py_date.fromisoformat(date_str)

    def get_date(self) -> py_date:
        """Get the Python date object."""
        return self._date

    def set_date(self, date_val: py_date) -> "Date":
        """Set the date value.

        Args:
            date_val: The new date

        Returns:
            Self for method chaining

        Raises:
            ValueError: If year is out of bounds
        """
        if date_val.year < 1 or date_val.year > 9999:
            raise ValueError(
                f"The year: {date_val.year} falls outside the accepted bounds of 0001-9999."
            )
        self._date = date_val
        if self.precision is None:
            self.precision = Precision.DAY
        return self

    def expand_partial_min_from_precision(self, precision: Precision) -> "Date":
        """Expand this partial date to minimum at the given precision.

        Args:
            precision: The precision to expand to

        Returns:
            A new Date with expanded minimums
        """
        d = self._date
        for i in range(precision.to_date_index() + 1, 3):
            if i == 1:  # Month
                d = d.replace(month=1)
            elif i == 2:  # Day
                d = d.replace(day=1)
        return Date(d, precision=precision)

    def expand_partial_min(self, precision: Precision) -> "Date":
        """Expand this partial date to minimum at the given precision.

        Args:
            precision: The precision to expand to

        Returns:
            A new Date with expanded minimums
        """
        return Date(self._date, precision=precision)

    def expand_partial_max(self, precision: Precision) -> "Date":
        """Expand this partial date to maximum at the given precision.

        Args:
            precision: The precision to expand to

        Returns:
            A new Date with expanded maximums
        """
        d = self._date
        for i in range(self.precision.to_date_index() + 1, 3):
            if i <= precision.to_date_index():
                # Set to maximum for this component
                if i == 1:  # Month
                    d = d.replace(month=12)
                elif i == 2:  # Day
                    # Get last day of month
                    if d.month == 12:
                        d = d.replace(year=d.year + 1, month=1, day=1)
                        d = d.replace(day=d.day - 1)
                    else:
                        next_month = d.replace(day=1, month=d.month + 1)
                        d = next_month.replace(day=next_month.day - 1)
            else:
                # Set to minimum
                if i == 1:  # Month
                    d = d.replace(month=1)
                elif i == 2:  # Day
                    d = d.replace(day=1)
        return Date(d, precision=precision)

    def compare(self, other: "BaseTemporal", for_sort: bool) -> Optional[int]:
        """Compare with another temporal value.

        Args:
            other: The other temporal value
            for_sort: Whether this is for sorting

        Returns:
            -1 if less, 0 if equal, 1 if greater, or None if uncertain
        """
        different_precisions = self.precision != other.precision

        if different_precisions:
            result = self.compare_to_precision(
                other, Precision.get_highest_date_precision(self.precision, other.precision)
            )
            if result is None and for_sort:
                return 1 if self.precision.to_date_index() > other.precision.to_date_index() else -1
            return result
        else:
            return self.compare_to_precision(other, self.precision)

    def compare_to_precision(self, other: "BaseTemporal", p: Precision) -> Optional[int]:
        """Compare at a specific precision.

        Args:
            other: The other temporal value
            p: The precision to use

        Returns:
            -1 if less, 0 if equal, 1 if greater, or None if uncertain
        """
        if not isinstance(other, Date):
            raise TypeError(f"Cannot compare Date with {type(other).__name__}")

        left_meets = self.precision.to_date_index() >= p.to_date_index()
        right_meets = other.precision.to_date_index() >= p.to_date_index()

        if not left_meets or not right_meets:
            p = Precision.get_lowest_date_precision(self.precision, other.precision)

        # Compare year, month, day
        date_components = [
            (self._date.year, other._date.year),
            (self._date.month, other._date.month),
            (self._date.day, other._date.day),
        ]

        for i in range(p.to_date_index() + 1):
            left_comp, right_comp = date_components[i]
            if left_comp > right_comp:
                return 1
            elif left_comp < right_comp:
                return -1

        if left_meets and right_meets:
            return 0

        return None

    def is_uncertain(self, p: Precision) -> bool:
        """Check if uncertain at the given precision.

        Args:
            p: The precision to check

        Returns:
            True if uncertain
        """
        if p == Precision.WEEK:
            p = Precision.DAY
        return self.precision.to_date_index() < p.to_date_index()

    def get_uncertainty_interval(self, p: Precision) -> "Interval":
        """Get the interval of uncertainty.

        Args:
            p: The precision to use

        Returns:
            An Interval representing the uncertainty
        """
        from .interval import Interval

        start = self.expand_partial_min(p)
        end = self.expand_partial_max(p).expand_partial_min_from_precision(p)
        return Interval(start, True, end, True)

    def __lt__(self, other: "BaseTemporal") -> bool:
        """Compare for less than."""
        result = self.compare(other, True)
        return result is not None and result < 0

    def __le__(self, other: "BaseTemporal") -> bool:
        """Compare for less than or equal."""
        result = self.compare(other, True)
        return result is not None and result <= 0

    def __gt__(self, other: "BaseTemporal") -> bool:
        """Compare for greater than."""
        result = self.compare(other, True)
        return result is not None and result > 0

    def __ge__(self, other: "BaseTemporal") -> bool:
        """Compare for greater than or equal."""
        result = self.compare(other, True)
        return result is not None and result >= 0

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Date):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((self._date, self.precision))

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if equivalent
        """
        if not isinstance(other, BaseTemporal):
            return False
        result = self.compare(other, False)
        return result is not None and result == 0

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if equal, False if not, None if uncertain
        """
        if not isinstance(other, BaseTemporal):
            return False
        result = self.compare(other, False)
        return None if result is None else result == 0

    def __str__(self) -> str:
        """Get string representation."""
        match self.precision:
            case Precision.YEAR:
                return f"{self._date.year:04d}"
            case Precision.MONTH:
                return f"{self._date.year:04d}-{self._date.month:02d}"
            case _:
                return f"{self._date.year:04d}-{self._date.month:02d}-{self._date.day:02d}"

    def to_python_date(self) -> py_date:
        """Convert to Python date object.

        Returns:
            Python date object
        """
        return self._date
