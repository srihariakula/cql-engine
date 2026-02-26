"""
Retrieve provider interface for CQL engine.

Provides data retrieval capabilities for CQL evaluation.
"""

from abc import ABC, abstractmethod
from typing import Iterable, Optional
from cql_engine.runtime.code import Code
from cql_engine.runtime.interval import Interval


class RetrieveProvider(ABC):
    """
    Interface for retrieving data during CQL evaluation.

    Implementations handle different data sources and provide unified retrieval semantics.
    """

    @abstractmethod
    def retrieve(
        self,
        context: str,
        context_path: Optional[str],
        context_value: object,
        data_type: str,
        template_id: Optional[str],
        code_path: Optional[str],
        codes: Optional[Iterable[Code]],
        value_set: Optional[str],
        date_path: Optional[str],
        date_low_path: Optional[str],
        date_high_path: Optional[str],
        date_range: Optional[Interval]
    ) -> Iterable[object]:
        """
        Retrieve data based on the specified criteria.

        Args:
            context: The evaluation context (e.g., "Patient")
            context_path: The path to the context on the retrieved object
            context_value: The value of the context
            data_type: The type of data to retrieve
            template_id: Optional template identifier for the data
            code_path: The path to the code property
            codes: The codes to match
            value_set: The value set to use for code matching
            date_path: The path to the date property
            date_low_path: The path to the low date of a date range
            date_high_path: The path to the high date of a date range
            date_range: The date range to filter by

        Returns:
            An iterable of objects matching the retrieval criteria
        """
        pass
