"""CQL Time type."""

from datetime import time as py_time
from typing import Optional

from .base_temporal import BaseTemporal
from .precision import Precision
from .temporal_helper import TemporalHelper


class Time(BaseTemporal):
    """Represents a CQL Time value.

    Times in CQL can have varying precision (hour through millisecond).
    """

    __slots__ = ("_time",)

    def __init__(
        self,
        time_or_hour: str | py_time | int,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        millisecond: Optional[int] = None,
        precision: Optional[Precision] = None,
    ):
        """Initialize a Time instance.

        Can be created from:
        - String: "14:30:00.123" or "14:30"
        - time: Python time object
        - Elements: hour, minute, second, millisecond

        Args:
            time_or_hour: The time value (string, time object, or hour int)
            minute: Minute (if time_or_hour is int)
            second: Second (if time_or_hour is int)
            millisecond: Millisecond (if time_or_hour is int)
            precision: The precision of this time

        Raises:
            ValueError: If time is invalid
        """
        super().__init__(precision)

        if isinstance(time_or_hour, str):
            self._time = self._parse_time_string(time_or_hour)
            if precision is None:
                # Infer precision from string format
                self.precision = self._infer_precision_from_string(time_or_hour)
        elif isinstance(time_or_hour, py_time):
            self._time = time_or_hour
            if precision is None:
                self.precision = Precision.MILLISECOND
        elif isinstance(time_or_hour, int):
            # Create from components
            minute = minute or 0
            second = second or 0
            millisecond = millisecond or 0
            # Convert millisecond to microsecond
            microsecond = millisecond * 1000
            self._time = py_time(time_or_hour, minute, second, microsecond)
            if precision is None:
                if millisecond:
                    self.precision = Precision.MILLISECOND
                elif second:
                    self.precision = Precision.SECOND
                elif minute:
                    self.precision = Precision.MINUTE
                else:
                    self.precision = Precision.HOUR

    @staticmethod
    def _infer_precision_from_string(time_str: str) -> Precision:
        """Infer precision from string format.

        Args:
            time_str: The time string

        Returns:
            The inferred Precision
        """
        time_str = time_str.replace("T", "")
        size = len(time_str.split(":"))
        if "." in time_str:
            size += 1
        return Precision.from_time_index(size - 1)

    @staticmethod
    def _parse_time_string(time_str: str) -> py_time:
        """Parse a time string.

        Args:
            time_str: The time string

        Returns:
            Python time object
        """
        time_str = time_str.replace("T", "")

        # Handle short formats (e.g., "14" or "1400")
        if time_str.isdigit():
            if len(time_str) == 2:
                time_str += ":00"
            elif len(time_str) == 4:
                time_str = time_str[:2] + ":" + time_str[2:]

        # Infer precision
        precision = Time._infer_precision_from_string(time_str)

        # Auto-complete
        time_str = TemporalHelper.auto_complete_time_string(time_str, precision)

        # Parse using ISO format
        return py_time.fromisoformat(time_str)

    def get_time(self) -> py_time:
        """Get the Python time object."""
        return self._time

    def set_time(self, time_val: py_time) -> "Time":
        """Set the time value.

        Args:
            time_val: The new time

        Returns:
            Self for method chaining
        """
        self._time = time_val
        if self.precision is None:
            self.precision = Precision.MILLISECOND
        return self

    def with_time(self, time_val: py_time) -> "Time":
        """Set time and return self.

        Args:
            time_val: The new time

        Returns:
            Self for method chaining
        """
        return self.set_time(time_val)

    def with_precision(self, precision: Precision) -> "Time":
        """Set precision and return self.

        Args:
            precision: The new precision

        Returns:
            Self for method chaining
        """
        self.precision = precision
        return self

    def expand_partial_min_from_precision(self, precision: Precision) -> "Time":
        """Expand to minimum at the given precision.

        Args:
            precision: The target precision

        Returns:
            A new Time with expanded minimums
        """
        t = self._time
        for i in range(precision.to_time_index() + 1, 4):
            t = self._set_time_component(t, i, "min")
        return Time(t, precision=self.precision)

    def expand_partial_min(self, precision: Optional[Precision] = None) -> "Time":
        """Expand to minimum at the given precision.

        Args:
            precision: The target precision

        Returns:
            A new Time with expanded minimums
        """
        return Time(self._time, precision=precision or Precision.MILLISECOND)

    def expand_partial_max(self, precision: Optional[Precision] = None) -> "Time":
        """Expand to maximum at the given precision.

        Args:
            precision: The target precision

        Returns:
            A new Time with expanded maximums
        """
        if precision is None:
            precision = Precision.MILLISECOND

        t = self._time
        for i in range(self.precision.to_time_index() + 1, 4):
            if i <= precision.to_time_index():
                t = self._set_time_component(t, i, "max")
            else:
                t = self._set_time_component(t, i, "min")

        return Time(t, precision=precision)

    @staticmethod
    def _set_time_component(t: py_time, component_index: int, value: str) -> py_time:
        """Set a time component to min or max value.

        Args:
            t: The time to modify
            component_index: The component index (0=hour, 1=minute, 2=second, 3=millisecond)
            value: Either "min" or "max"

        Returns:
            Modified time
        """
        if component_index == 0:  # Hour
            return t.replace(hour=0 if value == "min" else 23)
        elif component_index == 1:  # Minute
            return t.replace(minute=0 if value == "min" else 59)
        elif component_index == 2:  # Second
            return t.replace(second=0 if value == "min" else 59)
        elif component_index == 3:  # Millisecond
            return t.replace(microsecond=0 if value == "min" else 999999)
        return t

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
                other, Precision.get_highest_time_precision(self.precision, other.precision)
            )
            if result is None and for_sort:
                return (
                    1
                    if self.precision.to_time_index() > other.precision.to_time_index()
                    else -1
                )
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
        if not isinstance(other, Time):
            raise TypeError(f"Cannot compare Time with {type(other).__name__}")

        left_meets = self.precision.to_time_index() >= p.to_time_index()
        right_meets = other.precision.to_time_index() >= p.to_time_index()

        left_time = self._time
        right_time = other._time

        if not left_meets or not right_meets:
            p = Precision.get_lowest_time_precision(self.precision, other.precision)

        # Compare components
        components = [
            (left_time.hour, right_time.hour),
            (left_time.minute, right_time.minute),
            (left_time.second, right_time.second),
            (left_time.microsecond // 1000, right_time.microsecond // 1000),
        ]

        for i in range(p.to_time_index() + 1):
            left_comp, right_comp = components[i]
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
        return self.precision.to_time_index() < p.to_time_index()

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
        if not isinstance(other, Time):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((self._time, self.precision))

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
            case Precision.HOUR:
                return f"{self._time.hour:02d}"
            case Precision.MINUTE:
                return f"{self._time.hour:02d}:{self._time.minute:02d}"
            case Precision.SECOND:
                return f"{self._time.hour:02d}:{self._time.minute:02d}:{self._time.second:02d}"
            case _:
                return f"{self._time.hour:02d}:{self._time.minute:02d}:{self._time.second:02d}.{self._time.microsecond // 1000:03d}"

    def to_python_time(self) -> py_time:
        """Convert to Python time object.

        Returns:
            Python time object
        """
        return self._time
