"""Helper functions for temporal types."""

from decimal import Decimal
from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional
from zoneinfo import ZoneInfo

from .precision import Precision


class TemporalHelper:
    """Utility methods for temporal operations."""

    @staticmethod
    def normalize_datetime_elements(elements: Tuple[int, ...]) -> List[str]:
        """Normalize datetime elements to padded strings.

        Args:
            elements: Tuple of integer elements (year, month, day, hour, minute, second, millisecond)

        Returns:
            List of zero-padded string elements
        """
        result = []
        for i, element in enumerate(elements):
            if i == 0:  # Year
                result.append(str(element).zfill(4))
            elif i == 6:  # Millisecond
                result.append(str(element).zfill(3))
            else:
                result.append(str(element).zfill(2))
        return result

    @staticmethod
    def normalize_time_elements(elements: Tuple[int, ...]) -> List[str]:
        """Normalize time elements to padded strings.

        Args:
            elements: Tuple of integer elements (hour, minute, second, millisecond)

        Returns:
            List of zero-padded string elements
        """
        result = []
        for i, element in enumerate(elements):
            if i == 3:  # Millisecond
                result.append(str(element).zfill(3))
            else:
                result.append(str(element).zfill(2))
        return result

    @staticmethod
    def add_leading_zeros(element: int, length: int) -> str:
        """Add leading zeros to an element.

        Args:
            element: The element to pad
            length: The target length

        Returns:
            The zero-padded string
        """
        return str(element).zfill(length)

    @staticmethod
    def auto_complete_datetime_string(date_string: str, precision: Precision) -> str:
        """Auto-complete a datetime string to full precision.

        Args:
            date_string: The partial datetime string
            precision: The precision level of the string

        Returns:
            The auto-completed datetime string
        """
        completion_map = {
            Precision.YEAR: "-01-01T00:00:00.000",
            Precision.MONTH: "-01T00:00:00.000",
            Precision.DAY: "T00:00:00.000",
            Precision.HOUR: ":00:00.000",
            Precision.MINUTE: ":00.000",
            Precision.SECOND: ".000",
            Precision.MILLISECOND: "",
            Precision.WEEK: "T00:00:00.000",
        }
        return date_string + completion_map.get(precision, "")

    @staticmethod
    def auto_complete_date_string(date_string: str, precision: Precision) -> str:
        """Auto-complete a date string to full precision.

        Args:
            date_string: The partial date string
            precision: The precision level of the string

        Returns:
            The auto-completed date string
        """
        if precision == Precision.YEAR:
            return date_string + "-01-01"
        elif precision == Precision.MONTH:
            return date_string + "-01"
        return date_string

    @staticmethod
    def auto_complete_time_string(time_string: str, precision: Precision) -> str:
        """Auto-complete a time string to full precision.

        Args:
            time_string: The partial time string
            precision: The precision level of the string

        Returns:
            The auto-completed time string
        """
        if precision in (Precision.HOUR, Precision.MINUTE):
            return time_string + ":00.000"
        elif precision == Precision.SECOND:
            return time_string + ".000"
        return time_string

    @staticmethod
    def clean_array(elements: List[Optional[int]]) -> List[int]:
        """Remove None values from a list of integers.

        Args:
            elements: List of optional integers

        Returns:
            List with None values removed
        """
        return [e for e in elements if e is not None]

    @staticmethod
    def zone_to_offset(zone_offset: timezone) -> Decimal:
        """Convert a timezone offset to a decimal hour offset.

        Args:
            zone_offset: The timezone offset

        Returns:
            Decimal representing the hour offset
        """
        total_seconds = zone_offset.utcoffset(None).total_seconds()
        return Decimal(total_seconds / 3600)

    @staticmethod
    def weeks_to_days(weeks: int) -> int:
        """Convert weeks to days.

        Args:
            weeks: Number of weeks

        Returns:
            Number of days
        """
        years = weeks // 52
        weeks = weeks % 52
        return weeks * 7 + (years * 365)

    @staticmethod
    def truncate_value_to_target_precision(
        value: int, precision: Precision, target_precision: Precision
    ) -> int:
        """Truncate a value from one precision to another.

        Args:
            value: The value to truncate
            precision: The source precision
            target_precision: The target precision

        Returns:
            The truncated value
        """
        # Mapping of (source_precision, target_precision) to conversion factor
        conversion_map = {
            (Precision.YEAR, Precision.YEAR): 1,
            (Precision.MONTH, Precision.YEAR): 12,
            (Precision.DAY, Precision.YEAR): 365,
            (Precision.HOUR, Precision.YEAR): 365 * 24,
            (Precision.MINUTE, Precision.YEAR): 365 * 24 * 60,
            (Precision.SECOND, Precision.YEAR): 365 * 24 * 60 * 60,
            (Precision.MILLISECOND, Precision.YEAR): 365 * 24 * 60 * 60 * 1000,
            (Precision.YEAR, Precision.MONTH): 1 / 12,
            (Precision.MONTH, Precision.MONTH): 1,
            (Precision.DAY, Precision.MONTH): 30,
            (Precision.HOUR, Precision.MONTH): 30 * 24,
            (Precision.MINUTE, Precision.MONTH): 30 * 24 * 60,
            (Precision.SECOND, Precision.MONTH): 30 * 24 * 60 * 60,
            (Precision.MILLISECOND, Precision.MONTH): 30 * 24 * 60 * 60 * 1000,
            (Precision.YEAR, Precision.DAY): 1 / 365,
            (Precision.MONTH, Precision.DAY): 1 / 30,
            (Precision.DAY, Precision.DAY): 1,
            (Precision.HOUR, Precision.DAY): 24,
            (Precision.MINUTE, Precision.DAY): 24 * 60,
            (Precision.SECOND, Precision.DAY): 24 * 60 * 60,
            (Precision.MILLISECOND, Precision.DAY): 24 * 60 * 60 * 1000,
            (Precision.YEAR, Precision.HOUR): 1 / (365 * 24),
            (Precision.MONTH, Precision.HOUR): 1 / (30 * 24),
            (Precision.DAY, Precision.HOUR): 1 / 24,
            (Precision.HOUR, Precision.HOUR): 1,
            (Precision.MINUTE, Precision.HOUR): 60,
            (Precision.SECOND, Precision.HOUR): 60 * 60,
            (Precision.MILLISECOND, Precision.HOUR): 60 * 60 * 1000,
            (Precision.YEAR, Precision.MINUTE): 1 / (365 * 24 * 60),
            (Precision.MONTH, Precision.MINUTE): 1 / (30 * 24 * 60),
            (Precision.DAY, Precision.MINUTE): 1 / (24 * 60),
            (Precision.HOUR, Precision.MINUTE): 1 / 60,
            (Precision.MINUTE, Precision.MINUTE): 1,
            (Precision.SECOND, Precision.MINUTE): 60,
            (Precision.MILLISECOND, Precision.MINUTE): 60 * 1000,
            (Precision.YEAR, Precision.SECOND): 1 / (365 * 24 * 60 * 60),
            (Precision.MONTH, Precision.SECOND): 1 / (30 * 24 * 60 * 60),
            (Precision.DAY, Precision.SECOND): 1 / (24 * 60 * 60),
            (Precision.HOUR, Precision.SECOND): 1 / (60 * 60),
            (Precision.MINUTE, Precision.SECOND): 1 / 60,
            (Precision.SECOND, Precision.SECOND): 1,
            (Precision.MILLISECOND, Precision.SECOND): 1000,
            (Precision.YEAR, Precision.MILLISECOND): 1 / (365 * 24 * 60 * 60 * 1000),
            (Precision.MONTH, Precision.MILLISECOND): 1 / (30 * 24 * 60 * 60),
            (Precision.DAY, Precision.MILLISECOND): 1 / (24 * 60 * 60),
            (Precision.HOUR, Precision.MILLISECOND): 1 / (60 * 60),
            (Precision.MINUTE, Precision.MILLISECOND): 1 / 60,
            (Precision.SECOND, Precision.MILLISECOND): 1 / 1000,
            (Precision.MILLISECOND, Precision.MILLISECOND): 1,
        }

        factor = conversion_map.get((precision, target_precision), 1)
        return int(value * factor)
