"""Precision enumeration for temporal types."""

from enum import Enum
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional


class Precision(Enum):
    """Enumeration of temporal precision levels.

    Temporal types in CQL can have varying levels of precision. This enum
    defines the supported precision levels and provides conversion methods.
    """

    YEAR = "year"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"
    MILLISECOND = "millisecond"

    @staticmethod
    def from_string(precision_str: str) -> "Precision":
        """Convert a string to a Precision enum.

        Args:
            precision_str: The precision as a string

        Returns:
            The corresponding Precision enum value

        Raises:
            ValueError: If the precision string is invalid
        """
        precision_str = precision_str.lower()
        for precision in Precision:
            if precision.value.startswith(precision_str):
                return precision
        raise ValueError(f"Invalid precision: {precision_str}")

    @staticmethod
    def from_date_index(index: int) -> "Precision":
        """Convert a date precision index to a Precision enum.

        Args:
            index: The index (0=YEAR, 1=MONTH, 2=DAY)

        Returns:
            The corresponding Precision enum value

        Raises:
            ValueError: If the index is invalid
        """
        index_map = {0: Precision.YEAR, 1: Precision.MONTH, 2: Precision.DAY}
        if index not in index_map:
            raise ValueError(f"Invalid date precision index: {index}")
        return index_map[index]

    @staticmethod
    def from_datetime_index(index: int) -> "Precision":
        """Convert a datetime precision index to a Precision enum.

        Args:
            index: The index (0=YEAR, 1=MONTH, 2=DAY, 3=HOUR, 4=MINUTE, 5=SECOND, 6=MILLISECOND)

        Returns:
            The corresponding Precision enum value

        Raises:
            ValueError: If the index is invalid
        """
        index_map = {
            0: Precision.YEAR,
            1: Precision.MONTH,
            2: Precision.DAY,
            3: Precision.HOUR,
            4: Precision.MINUTE,
            5: Precision.SECOND,
            6: Precision.MILLISECOND,
        }
        if index not in index_map:
            raise ValueError(f"Invalid datetime precision index: {index}")
        return index_map[index]

    @staticmethod
    def from_time_index(index: int) -> "Precision":
        """Convert a time precision index to a Precision enum.

        Args:
            index: The index (0=HOUR, 1=MINUTE, 2=SECOND, 3=MILLISECOND)

        Returns:
            The corresponding Precision enum value
        """
        return Precision.from_datetime_index(index + 3)

    def to_date_index(self) -> int:
        """Convert this precision to a date index.

        Returns:
            The date index (0=YEAR, 1=MONTH, 2=DAY)
        """
        index_map = {
            Precision.YEAR: 0,
            Precision.MONTH: 1,
            Precision.DAY: 2,
            Precision.WEEK: 2,
            Precision.HOUR: 2,
            Precision.MINUTE: 2,
            Precision.SECOND: 2,
            Precision.MILLISECOND: 2,
        }
        return index_map[self]

    def to_datetime_index(self) -> int:
        """Convert this precision to a datetime index.

        Returns:
            The datetime index (0=YEAR, 1=MONTH, 2=DAY, 3=HOUR, 4=MINUTE, 5=SECOND, 6=MILLISECOND)
        """
        index_map = {
            Precision.YEAR: 0,
            Precision.MONTH: 1,
            Precision.DAY: 2,
            Precision.WEEK: 2,
            Precision.HOUR: 3,
            Precision.MINUTE: 4,
            Precision.SECOND: 5,
            Precision.MILLISECOND: 6,
        }
        return index_map[self]

    def to_time_index(self) -> int:
        """Convert this precision to a time index.

        Returns:
            The time index (0=HOUR, 1=MINUTE, 2=SECOND, 3=MILLISECOND)
        """
        index_map = {
            Precision.HOUR: 0,
            Precision.MINUTE: 1,
            Precision.SECOND: 2,
            Precision.MILLISECOND: 3,
        }
        return index_map.get(self, 3)

    def get_next_precision(self) -> "Precision":
        """Get the next more precise precision level.

        Returns:
            The next Precision, or MILLISECOND if already at the most precise
        """
        next_map = {
            Precision.YEAR: Precision.MONTH,
            Precision.MONTH: Precision.DAY,
            Precision.WEEK: Precision.DAY,
            Precision.DAY: Precision.HOUR,
            Precision.HOUR: Precision.MINUTE,
            Precision.MINUTE: Precision.SECOND,
            Precision.SECOND: Precision.MILLISECOND,
            Precision.MILLISECOND: Precision.MILLISECOND,
        }
        return next_map[self]

    @staticmethod
    def get_lowest_date_precision(p1: "Precision", p2: "Precision") -> "Precision":
        """Get the lowest (least precise) of two date precisions."""
        return p1 if p1.to_date_index() < p2.to_date_index() else p2

    @staticmethod
    def get_highest_date_precision(p1: "Precision", p2: "Precision") -> "Precision":
        """Get the highest (most precise) of two date precisions."""
        return p1 if p1.to_date_index() > p2.to_date_index() else p2

    @staticmethod
    def get_lowest_datetime_precision(p1: "Precision", p2: "Precision") -> "Precision":
        """Get the lowest (least precise) of two datetime precisions."""
        return p1 if p1.to_datetime_index() < p2.to_datetime_index() else p2

    @staticmethod
    def get_highest_datetime_precision(p1: "Precision", p2: "Precision") -> "Precision":
        """Get the highest (most precise) of two datetime precisions."""
        return p1 if p1.to_datetime_index() > p2.to_datetime_index() else p2

    @staticmethod
    def get_lowest_time_precision(p1: "Precision", p2: "Precision") -> "Precision":
        """Get the lowest (least precise) of two time precisions."""
        return p1 if p1.to_time_index() < p2.to_time_index() else p2

    @staticmethod
    def get_highest_time_precision(p1: "Precision", p2: "Precision") -> "Precision":
        """Get the highest (most precise) of two time precisions."""
        return p1 if p1.to_time_index() > p2.to_time_index() else p2

    def __str__(self) -> str:
        """Return the string representation of this precision."""
        return self.value
