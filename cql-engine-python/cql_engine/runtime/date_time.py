"""CQL DateTime type."""

from datetime import datetime as py_datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional

from .base_temporal import BaseTemporal
from .precision import Precision
from .temporal_helper import TemporalHelper


class DateTime(BaseTemporal):
    """Represents a CQL DateTime value.

    DateTimes in CQL can have varying precision (year through millisecond).
    """

    __slots__ = ("_datetime",)

    def __init__(
        self,
        dt: str | py_datetime,
        precision: Optional[Precision] = None,
        offset: Optional[timezone] = None,
        *elements: int,
    ):
        """Initialize a DateTime instance.

        Can be created from:
        - String: "2021-05-15T14:30:00" or "2021-05-15"
        - datetime: Python datetime object
        - Elements: year, month, day, hour, minute, second, millisecond

        Args:
            dt: The datetime value (string or datetime object)
            precision: The precision of this datetime
            offset: The timezone offset
            elements: Optional elements if creating from components

        Raises:
            ValueError: If datetime is invalid or year is out of bounds
        """
        super().__init__(precision, offset)

        if isinstance(dt, str):
            self._datetime = self._parse_datetime_string(dt, offset)
            if precision is None:
                # Infer precision from string format
                self.precision = self._infer_precision_from_string(dt)
        elif isinstance(dt, py_datetime):
            self._datetime = dt
            if precision is None:
                self.precision = Precision.MILLISECOND
        elif isinstance(dt, (int, Decimal)):
            # Creating from elements
            self._datetime = self._create_from_elements(dt, offset, *elements)
            if precision is None:
                self.precision = Precision.MILLISECOND

        # Validate year bounds
        if self._datetime.year < 1 or self._datetime.year > 9999:
            raise ValueError(
                f"The year: {self._datetime.year} falls outside the accepted bounds of 0001-9999."
            )

    @staticmethod
    def _infer_precision_from_string(dt_str: str) -> Precision:
        """Infer precision from string format.

        Args:
            dt_str: The datetime string

        Returns:
            The inferred Precision
        """
        if "T" in dt_str:
            parts = dt_str.split("T")
            date_parts = parts[0].split("-")
            size = len(date_parts)
            time_part = parts[1] if len(parts) > 1 else ""
            time_parts = time_part.split(":") if time_part else []
            size += len(time_parts)
            if "." in time_part:
                size += 1
        else:
            size = len(dt_str.split("-"))

        return Precision.from_datetime_index(size - 1)

    @staticmethod
    def _parse_datetime_string(dt_str: str, offset: Optional[timezone] = None) -> py_datetime:
        """Parse a datetime string.

        Args:
            dt_str: The datetime string
            offset: Optional timezone offset

        Returns:
            Python datetime object
        """
        # Handle partial datetime strings
        has_tz = "Z" in dt_str or "+" in dt_str or dt_str.count("-") > 2

        # Auto-complete the string
        precision = DateTime._infer_precision_from_string(dt_str)
        dt_str = TemporalHelper.auto_complete_datetime_string(dt_str, precision)

        if has_tz:
            return py_datetime.fromisoformat(dt_str)
        elif offset:
            dt_str += offset.tzname(None)
            return py_datetime.fromisoformat(dt_str)
        else:
            # Parse as naive and use system timezone
            return py_datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)

    @staticmethod
    def _create_from_elements(
        offset: int | Decimal,
        elements_start_idx: int | Decimal,
        *elements: int,
    ) -> py_datetime:
        """Create datetime from individual elements.

        Args:
            offset: The timezone offset
            elements_start_idx: Unused (matches Java signature)
            elements: year, month, day, hour, minute, second, millisecond

        Returns:
            Python datetime object
        """
        if not elements:
            raise ValueError("DateTime must include at least a year")

        # Normalize elements to strings with padding
        str_elements = TemporalHelper.normalize_datetime_elements(elements)

        # Build datetime string
        dt_str = str_elements[0]
        if len(str_elements) > 1:
            dt_str += f"-{str_elements[1]}"
        if len(str_elements) > 2:
            dt_str += f"-{str_elements[2]}"
        if len(str_elements) > 3:
            dt_str += f"T{str_elements[3]}"
        if len(str_elements) > 4:
            dt_str += f":{str_elements[4]}"
        if len(str_elements) > 5:
            dt_str += f":{str_elements[5]}"
        if len(str_elements) > 6:
            dt_str += f".{str_elements[6]}"

        # Auto-complete
        precision = Precision.from_datetime_index(len(str_elements) - 1)
        dt_str = TemporalHelper.auto_complete_datetime_string(dt_str, precision)

        # Add offset if provided
        if offset is not None:
            if isinstance(offset, Decimal):
                hours = int(offset)
                minutes = int((offset % 1) * 60)
            else:
                hours = int(offset)
                minutes = int((offset % 1) * 60)

            tz = timezone(timedelta(hours=hours, minutes=minutes))
            dt_str += f"{tz.tzname(None)}"

        return py_datetime.fromisoformat(dt_str)

    def get_datetime(self) -> py_datetime:
        """Get the Python datetime object."""
        return self._datetime

    def set_datetime(self, dt: py_datetime) -> "DateTime":
        """Set the datetime value.

        Args:
            dt: The new datetime

        Returns:
            Self for method chaining

        Raises:
            ValueError: If year is out of bounds
        """
        if dt.year < 1 or dt.year > 9999:
            raise ValueError(
                f"The year: {dt.year} falls outside the accepted bounds of 0001-9999."
            )
        self._datetime = dt
        return self

    def with_datetime(self, dt: py_datetime) -> "DateTime":
        """Set datetime and return self.

        Args:
            dt: The new datetime

        Returns:
            Self for method chaining
        """
        return self.set_datetime(dt)

    def with_precision(self, precision: Precision) -> "DateTime":
        """Set precision and return self.

        Args:
            precision: The new precision

        Returns:
            Self for method chaining
        """
        self.precision = precision
        return self

    def expand_partial_min_from_precision(self, precision: Precision) -> "DateTime":
        """Expand to minimum at the given precision.

        Args:
            precision: The target precision

        Returns:
            A new DateTime with expanded minimums
        """
        dt = self._datetime
        for i in range(precision.to_datetime_index() + 1, 7):
            dt = self._set_datetime_component(dt, i, "min")
        return DateTime(dt, self.precision)

    def expand_partial_min(self, precision: Optional[Precision] = None) -> "DateTime":
        """Expand to minimum at the given precision.

        Args:
            precision: The target precision

        Returns:
            A new DateTime with expanded minimums
        """
        return DateTime(self._datetime, precision or Precision.MILLISECOND)

    def expand_partial_max(self, precision: Optional[Precision] = None) -> "DateTime":
        """Expand to maximum at the given precision.

        Args:
            precision: The target precision

        Returns:
            A new DateTime with expanded maximums
        """
        if precision is None:
            precision = Precision.MILLISECOND

        dt = self._datetime
        for i in range(self.precision.to_datetime_index() + 1, 7):
            if i <= precision.to_datetime_index():
                dt = self._set_datetime_component(dt, i, "max")
            else:
                dt = self._set_datetime_component(dt, i, "min")

        return DateTime(dt, precision)

    @staticmethod
    def _set_datetime_component(
        dt: py_datetime, component_index: int, value: str
    ) -> py_datetime:
        """Set a datetime component to min or max value.

        Args:
            dt: The datetime to modify
            component_index: The component index (0=year, 1=month, ..., 6=millisecond)
            value: Either "min" or "max"

        Returns:
            Modified datetime
        """
        if component_index == 0:  # Year
            return dt.replace(year=1 if value == "min" else 9999)
        elif component_index == 1:  # Month
            return dt.replace(month=1 if value == "min" else 12)
        elif component_index == 2:  # Day
            if value == "min":
                return dt.replace(day=1)
            else:
                # Last day of month
                next_month = (dt.replace(day=1) + timedelta(days=32)).replace(day=1)
                return next_month - timedelta(days=1)
        elif component_index == 3:  # Hour
            return dt.replace(hour=0 if value == "min" else 23)
        elif component_index == 4:  # Minute
            return dt.replace(minute=0 if value == "min" else 59)
        elif component_index == 5:  # Second
            return dt.replace(second=0 if value == "min" else 59)
        elif component_index == 6:  # Millisecond
            return dt.replace(microsecond=0 if value == "min" else 999999)
        return dt

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
                other, Precision.get_highest_datetime_precision(self.precision, other.precision)
            )
            if result is None and for_sort:
                return (
                    1
                    if self.precision.to_datetime_index() > other.precision.to_datetime_index()
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
        if not isinstance(other, DateTime):
            raise TypeError(f"Cannot compare DateTime with {type(other).__name__}")

        left_meets = self.precision.to_datetime_index() >= p.to_datetime_index()
        right_meets = other.precision.to_datetime_index() >= p.to_datetime_index()

        left_dt = self._get_normalized(self._datetime, p)
        right_dt = other._get_normalized(other._datetime, p)

        if not left_meets or not right_meets:
            p = Precision.get_lowest_datetime_precision(self.precision, other.precision)

        # Compare components
        components = [
            (left_dt.year, right_dt.year),
            (left_dt.month, right_dt.month),
            (left_dt.day, right_dt.day),
            (left_dt.hour, right_dt.hour),
            (left_dt.minute, right_dt.minute),
            (left_dt.second, right_dt.second),
            (left_dt.microsecond // 1000, right_dt.microsecond // 1000),
        ]

        for i in range(p.to_datetime_index() + 1):
            left_comp, right_comp = components[i]
            if left_comp > right_comp:
                return 1
            elif left_comp < right_comp:
                return -1

        if left_meets and right_meets:
            return 0

        return None

    @staticmethod
    def _get_normalized(dt: py_datetime, precision: Precision) -> py_datetime:
        """Get normalized datetime at a given precision.

        Args:
            dt: The datetime to normalize
            precision: The precision

        Returns:
            Normalized datetime
        """
        if precision.to_datetime_index() > Precision.DAY.to_datetime_index():
            # Convert to system timezone if needed
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt
        return dt

    def is_uncertain(self, p: Precision) -> bool:
        """Check if uncertain at the given precision.

        Args:
            p: The precision to check

        Returns:
            True if uncertain
        """
        if p == Precision.WEEK:
            p = Precision.DAY
        return self.precision.to_datetime_index() < p.to_datetime_index()

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
        if not isinstance(other, DateTime):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((self._datetime, self.precision))

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
                return f"{self._datetime.year:04d}"
            case Precision.MONTH:
                return f"{self._datetime.year:04d}-{self._datetime.month:02d}"
            case Precision.DAY:
                return (
                    f"{self._datetime.year:04d}-{self._datetime.month:02d}-{self._datetime.day:02d}"
                )
            case Precision.HOUR:
                return f"{self._datetime.year:04d}-{self._datetime.month:02d}-{self._datetime.day:02d}T{self._datetime.hour:02d}"
            case Precision.MINUTE:
                return f"{self._datetime.year:04d}-{self._datetime.month:02d}-{self._datetime.day:02d}T{self._datetime.hour:02d}:{self._datetime.minute:02d}"
            case Precision.SECOND:
                return f"{self._datetime.year:04d}-{self._datetime.month:02d}-{self._datetime.day:02d}T{self._datetime.hour:02d}:{self._datetime.minute:02d}:{self._datetime.second:02d}"
            case _:
                return f"{self._datetime.year:04d}-{self._datetime.month:02d}-{self._datetime.day:02d}T{self._datetime.hour:02d}:{self._datetime.minute:02d}:{self._datetime.second:02d}.{self._datetime.microsecond // 1000:03d}"

    def to_python_datetime(self) -> py_datetime:
        """Convert to Python datetime object.

        Returns:
            Python datetime object
        """
        return self._datetime
