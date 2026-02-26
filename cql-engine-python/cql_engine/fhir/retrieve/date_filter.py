"""Date filter for FHIR retrieval."""

from dataclasses import dataclass
from typing import Optional

# Assuming Interval is from cql_engine runtime
# from cql_engine.runtime import Interval


@dataclass
class DateFilter:
    """Filter for date-based FHIR searches.

    Attributes:
        date_path: Path to the date element
        date_low_path: Path to the low date bound
        date_high_path: Path to the high date bound
        date_range: Interval representing the date range
    """

    date_path: Optional[str] = None
    date_low_path: Optional[str] = None
    date_high_path: Optional[str] = None
    date_range: Optional[object] = None  # Interval

    def get_date_path(self) -> Optional[str]:
        """Get the date path."""
        return self.date_path

    def get_date_low_path(self) -> Optional[str]:
        """Get the low date path."""
        return self.date_low_path

    def get_date_high_path(self) -> Optional[str]:
        """Get the high date path."""
        return self.date_high_path

    def get_date_range(self) -> Optional[object]:
        """Get the date range interval."""
        return self.date_range
