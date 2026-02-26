"""Base class for temporal types (Date, DateTime, Time)."""

from abc import ABC, abstractmethod
from datetime import timezone
from typing import Optional, TYPE_CHECKING

from .cql_type import CqlType
from .precision import Precision

if TYPE_CHECKING:
    from .interval import Interval


class BaseTemporal(CqlType, ABC):
    """Base class for all temporal types.

    Temporal types include Date, DateTime, and Time. They share common
    functionality for precision and evaluation offset handling.
    """

    __slots__ = ("precision", "evaluation_offset")

    def __init__(self, precision: Optional[Precision] = None, evaluation_offset: Optional[timezone] = None):
        """Initialize a BaseTemporal instance.

        Args:
            precision: The precision of this temporal value
            evaluation_offset: The timezone offset for evaluation
        """
        self.precision = precision
        self.evaluation_offset = evaluation_offset

    def get_precision(self) -> Optional[Precision]:
        """Get the precision of this temporal value."""
        return self.precision

    def set_precision(self, precision: Precision) -> "BaseTemporal":
        """Set the precision of this temporal value.

        Args:
            precision: The new precision

        Returns:
            Self for method chaining
        """
        self.precision = precision
        return self

    def get_evaluation_offset(self) -> Optional[timezone]:
        """Get the evaluation timezone offset."""
        return self.evaluation_offset

    def set_evaluation_offset(self, offset: timezone) -> None:
        """Set the evaluation timezone offset.

        Args:
            offset: The timezone offset
        """
        self.evaluation_offset = offset

    @staticmethod
    def get_highest_precision(*values: "BaseTemporal") -> str:
        """Get the highest (most precise) precision among the given values.

        Args:
            values: Variable number of BaseTemporal instances

        Returns:
            The string representation of the highest precision
        """
        if not values:
            return str(Precision.MILLISECOND)

        max_index = -1
        is_datetime = True
        is_date = False

        for value in values:
            if isinstance(value, type) and hasattr(value, "__name__"):
                class_name = value.__name__
            else:
                class_name = value.__class__.__name__

            if class_name == "DateTime":
                if value.precision.to_datetime_index() > max_index:
                    max_index = value.precision.to_datetime_index()
            elif class_name == "Date":
                is_datetime = False
                is_date = True
                if value.precision.to_date_index() > max_index:
                    max_index = value.precision.to_date_index()
            elif class_name == "Time":
                is_datetime = False
                if value.precision.to_time_index() > max_index:
                    max_index = value.precision.to_time_index()

        if max_index == -1:
            return str(Precision.MILLISECOND)

        if is_datetime:
            return str(Precision.from_datetime_index(max_index))
        elif is_date:
            return str(Precision.from_date_index(max_index))
        else:
            return str(Precision.from_time_index(max_index))

    @staticmethod
    def get_lowest_precision(*values: "BaseTemporal") -> str:
        """Get the lowest (least precise) precision among the given values.

        Args:
            values: Variable number of BaseTemporal instances

        Returns:
            The string representation of the lowest precision
        """
        if not values:
            return str(Precision.YEAR)

        min_index = 99
        is_datetime = True
        is_date = False

        for value in values:
            if isinstance(value, type) and hasattr(value, "__name__"):
                class_name = value.__name__
            else:
                class_name = value.__class__.__name__

            if class_name == "DateTime":
                if value.precision.to_datetime_index() < min_index:
                    min_index = value.precision.to_datetime_index()
            elif class_name == "Date":
                is_datetime = False
                is_date = True
                if value.precision.to_date_index() < min_index:
                    min_index = value.precision.to_date_index()
            elif class_name == "Time":
                is_datetime = False
                if value.precision.to_time_index() < min_index:
                    min_index = value.precision.to_time_index()

        if min_index == 99:
            return str(Precision.YEAR)

        if is_datetime:
            return str(Precision.from_datetime_index(min_index))
        elif is_date:
            return str(Precision.from_date_index(min_index))
        else:
            return str(Precision.from_time_index(min_index))

    @abstractmethod
    def compare(self, other: "BaseTemporal", for_sort: bool) -> Optional[int]:
        """Compare this temporal value with another.

        Args:
            other: The other temporal value to compare
            for_sort: Whether this is being used for sorting

        Returns:
            -1 if less, 0 if equal, 1 if greater, or None if uncertain
        """
        ...

    @abstractmethod
    def compare_to_precision(self, other: "BaseTemporal", p: Precision) -> Optional[int]:
        """Compare this temporal value with another at a specific precision.

        Args:
            other: The other temporal value to compare
            p: The precision to use for comparison

        Returns:
            -1 if less, 0 if equal, 1 if greater, or None if uncertain
        """
        ...

    @abstractmethod
    def is_uncertain(self, p: Precision) -> bool:
        """Check if this value is uncertain at the given precision.

        Args:
            p: The precision to check

        Returns:
            True if uncertain at this precision
        """
        ...

    @abstractmethod
    def get_uncertainty_interval(self, p: Precision) -> "Interval":
        """Get the interval of uncertainty at the given precision.

        Args:
            p: The precision to use

        Returns:
            An Interval representing the uncertainty
        """
        ...

    @abstractmethod
    def __lt__(self, other: "BaseTemporal") -> bool:
        """Compare for less than."""
        ...

    @abstractmethod
    def __le__(self, other: "BaseTemporal") -> bool:
        """Compare for less than or equal."""
        ...

    @abstractmethod
    def __gt__(self, other: "BaseTemporal") -> bool:
        """Compare for greater than."""
        ...

    @abstractmethod
    def __ge__(self, other: "BaseTemporal") -> bool:
        """Compare for greater than or equal."""
        ...

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        ...
