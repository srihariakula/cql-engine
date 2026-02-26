"""Abstract interface for FHIR-to-CQL type conversion."""

from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional
from decimal import Decimal


class FhirTypeConverter(ABC):
    """Abstract base class for FHIR-to-CQL type conversion.

    Provides bidirectional conversion between FHIR and CQL types.
    Implementations must handle version-specific FHIR types.
    """

    # CQL-to-FHIR conversions

    @abstractmethod
    def is_fhir_type(self, value: Any) -> bool:
        """Check if a value is a FHIR type.

        Args:
            value: Value to test

        Returns:
            True if value is a FHIR type

        Raises:
            TypeError: If value is None
        """
        pass

    @abstractmethod
    def to_fhir_type(self, value: Any) -> Any:
        """Convert a CQL value to a FHIR type.

        Args:
            value: CQL value to convert

        Returns:
            FHIR type

        Raises:
            ValueError: If value is an Iterable
        """
        pass

    @abstractmethod
    def to_fhir_types(self, values: Iterable[Any]) -> Iterable[Any]:
        """Convert CQL values to FHIR types.

        Preserves ordering, nulls, and nested lists.

        Args:
            values: Iterable of CQL values

        Returns:
            Iterable of FHIR types
        """
        pass

    @abstractmethod
    def to_fhir_id(self, value: str) -> Any:
        """Convert a string to FHIR Id.

        Args:
            value: String value

        Returns:
            FHIR Id type
        """
        pass

    @abstractmethod
    def to_fhir_boolean(self, value: Optional[bool]) -> Any:
        """Convert a boolean to FHIR Boolean.

        Args:
            value: Boolean value

        Returns:
            FHIR Boolean type
        """
        pass

    @abstractmethod
    def to_fhir_integer(self, value: Optional[int]) -> Any:
        """Convert an integer to FHIR Integer.

        Args:
            value: Integer value

        Returns:
            FHIR Integer type
        """
        pass

    @abstractmethod
    def to_fhir_decimal(self, value: Optional[Decimal]) -> Any:
        """Convert a decimal to FHIR Decimal.

        Args:
            value: Decimal value

        Returns:
            FHIR Decimal type
        """
        pass

    @abstractmethod
    def to_fhir_date(self, value: Any) -> Any:
        """Convert a CQL Date to FHIR Date.

        Args:
            value: CQL Date

        Returns:
            FHIR Date type
        """
        pass

    @abstractmethod
    def to_fhir_datetime(self, value: Any) -> Any:
        """Convert a CQL DateTime to FHIR DateTime.

        Args:
            value: CQL DateTime

        Returns:
            FHIR DateTime type
        """
        pass

    @abstractmethod
    def to_fhir_time(self, value: Any) -> Any:
        """Convert a CQL Time to FHIR Time.

        Args:
            value: CQL Time

        Returns:
            FHIR Time type
        """
        pass

    @abstractmethod
    def to_fhir_string(self, value: Optional[str]) -> Any:
        """Convert a string to FHIR String.

        Args:
            value: String value

        Returns:
            FHIR String type
        """
        pass

    @abstractmethod
    def to_fhir_quantity(self, value: Any) -> Any:
        """Convert a CQL Quantity to FHIR Quantity.

        Args:
            value: CQL Quantity

        Returns:
            FHIR Quantity type
        """
        pass

    @abstractmethod
    def to_fhir_ratio(self, value: Any) -> Any:
        """Convert a CQL Ratio to FHIR Ratio.

        Args:
            value: CQL Ratio

        Returns:
            FHIR Ratio type
        """
        pass

    @abstractmethod
    def to_fhir_any(self, value: Any) -> Any:
        """Convert a CQL Any to FHIR.

        Args:
            value: CQL value

        Returns:
            FHIR type
        """
        pass

    @abstractmethod
    def to_fhir_coding(self, value: Any) -> Any:
        """Convert a CQL Code to FHIR Coding.

        Args:
            value: CQL Code

        Returns:
            FHIR Coding type
        """
        pass

    @abstractmethod
    def to_fhir_codeable_concept(self, value: Any) -> Any:
        """Convert a CQL Concept to FHIR CodeableConcept.

        Args:
            value: CQL Concept

        Returns:
            FHIR CodeableConcept type
        """
        pass

    @abstractmethod
    def to_fhir_period(self, value: Any) -> Any:
        """Convert a CQL Interval to FHIR Period.

        Args:
            value: CQL Interval (Date or DateTime)

        Returns:
            FHIR Period type
        """
        pass

    @abstractmethod
    def to_fhir_range(self, value: Any) -> Any:
        """Convert a CQL Interval to FHIR Range.

        Args:
            value: CQL Interval (Quantity)

        Returns:
            FHIR Range type
        """
        pass

    @abstractmethod
    def to_fhir_interval(self, value: Any) -> Any:
        """Convert a CQL Interval to FHIR Range or Period.

        Args:
            value: CQL Interval

        Returns:
            FHIR Range or Period
        """
        pass

    @abstractmethod
    def to_fhir_tuple(self, value: Any) -> Any:
        """Convert a CQL Tuple to FHIR Structure.

        Args:
            value: CQL Tuple

        Returns:
            FHIR structure
        """
        pass

    # FHIR-to-CQL conversions

    @abstractmethod
    def is_cql_type(self, value: Any) -> bool:
        """Check if a value is a CQL type.

        Args:
            value: Value to test

        Returns:
            True if value is a CQL type

        Raises:
            TypeError: If value is None
        """
        pass

    @abstractmethod
    def to_cql_type(self, value: Any) -> Any:
        """Convert a FHIR value to CQL type.

        Args:
            value: FHIR value

        Returns:
            CQL type

        Raises:
            ValueError: If value is an Iterable
        """
        pass

    @abstractmethod
    def to_cql_types(self, values: Iterable[Any]) -> Iterable[Any]:
        """Convert FHIR values to CQL types.

        Preserves ordering, nulls, and nested lists.

        Args:
            values: Iterable of FHIR values

        Returns:
            Iterable of CQL types
        """
        pass

    @abstractmethod
    def to_cql_id(self, value: Any) -> Optional[str]:
        """Convert FHIR Id to string.

        Args:
            value: FHIR Id

        Returns:
            String value
        """
        pass

    @abstractmethod
    def to_cql_boolean(self, value: Any) -> Optional[bool]:
        """Convert FHIR Boolean to Python boolean.

        Args:
            value: FHIR Boolean

        Returns:
            Python bool
        """
        pass

    @abstractmethod
    def to_cql_integer(self, value: Any) -> Optional[int]:
        """Convert FHIR Integer to Python int.

        Args:
            value: FHIR Integer

        Returns:
            Python int
        """
        pass

    @abstractmethod
    def to_cql_decimal(self, value: Any) -> Optional[Decimal]:
        """Convert FHIR Decimal to Decimal.

        Args:
            value: FHIR Decimal

        Returns:
            Python Decimal
        """
        pass

    @abstractmethod
    def to_cql_date(self, value: Any) -> Any:
        """Convert FHIR Date to CQL Date.

        Args:
            value: FHIR Date

        Returns:
            CQL Date

        Raises:
            ValueError: If not a Date
        """
        pass

    @abstractmethod
    def to_cql_datetime(self, value: Any) -> Any:
        """Convert FHIR DateTime to CQL DateTime.

        Args:
            value: FHIR DateTime

        Returns:
            CQL DateTime

        Raises:
            ValueError: If not a DateTime
        """
        pass

    @abstractmethod
    def to_cql_temporal(self, value: Any) -> Any:
        """Convert FHIR DateTime, Date, or Instant to CQL BaseTemporal.

        Args:
            value: FHIR temporal value

        Returns:
            CQL BaseTemporal

        Raises:
            ValueError: If not a temporal type
        """
        pass

    @abstractmethod
    def to_cql_time(self, value: Any) -> Any:
        """Convert FHIR Time to CQL Time.

        Args:
            value: FHIR Time

        Returns:
            CQL Time

        Raises:
            ValueError: If not a Time
        """
        pass

    @abstractmethod
    def to_cql_string(self, value: Any) -> Optional[str]:
        """Convert FHIR String to Python str.

        Args:
            value: FHIR String

        Returns:
            Python str
        """
        pass

    @abstractmethod
    def to_cql_quantity(self, value: Any) -> Any:
        """Convert FHIR Quantity to CQL Quantity.

        Args:
            value: FHIR Quantity

        Returns:
            CQL Quantity

        Raises:
            ValueError: If not a Quantity
        """
        pass

    @abstractmethod
    def to_cql_ratio(self, value: Any) -> Any:
        """Convert FHIR Ratio to CQL Ratio.

        Args:
            value: FHIR Ratio

        Returns:
            CQL Ratio

        Raises:
            ValueError: If not a Ratio
        """
        pass

    @abstractmethod
    def to_cql_any(self, value: Any) -> Any:
        """Convert FHIR type to CQL.

        Args:
            value: FHIR value

        Returns:
            CQL value
        """
        pass

    @abstractmethod
    def to_cql_code(self, value: Any) -> Any:
        """Convert FHIR Coding to CQL Code.

        Args:
            value: FHIR Coding

        Returns:
            CQL Code
        """
        pass

    @abstractmethod
    def to_cql_concept(self, value: Any) -> Any:
        """Convert FHIR CodeableConcept to CQL Concept.

        Args:
            value: FHIR CodeableConcept

        Returns:
            CQL Concept

        Raises:
            ValueError: If not a CodeableConcept
        """
        pass

    @abstractmethod
    def to_cql_interval(self, value: Any) -> Any:
        """Convert FHIR Range or Period to CQL Interval.

        Args:
            value: FHIR Range or Period

        Returns:
            CQL Interval

        Raises:
            ValueError: If not a Range or Period
        """
        pass

    @abstractmethod
    def to_cql_tuple(self, value: Any) -> Any:
        """Convert FHIR Structure to CQL Tuple.

        Args:
            value: FHIR structure

        Returns:
            CQL Tuple
        """
        pass
