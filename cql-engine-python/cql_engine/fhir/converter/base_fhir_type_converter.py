"""Base implementation for FHIR-to-CQL type conversion."""

from abc import abstractmethod
from typing import Any, Iterable, List, Optional
from decimal import Decimal
from calendar import Calendar
from datetime import datetime, time
from zoneinfo import ZoneInfo

from .fhir_type_converter import FhirTypeConverter


class BaseFhirTypeConverter(FhirTypeConverter):
    """Abstract base class with common FHIR-to-CQL conversion logic.

    Implements shared conversion logic for all FHIR versions.
    Version-specific subclasses implement primitive type constructors.
    """

    def is_fhir_type(self, value: Any) -> bool:
        """Check if a value is a FHIR type.

        Args:
            value: Value to test

        Returns:
            True if value is a FHIR type

        Raises:
            TypeError: If value is None
        """
        if value is None:
            raise TypeError("value cannot be None")

        if isinstance(value, Iterable) and not isinstance(value, str):
            raise ValueError("is_fhir_type cannot be used for Iterables")

        # FHIR types typically inherit from IBase or have resource_type
        return hasattr(value, "resource_type") or isinstance(value, dict) and "resourceType" in value

    def to_fhir_types(self, values: Iterable[Any]) -> Iterable[Any]:
        """Convert CQL values to FHIR types.

        Args:
            values: Iterable of CQL values

        Returns:
            Iterable of FHIR types
        """
        converted = []

        for value in values:
            if value is None:
                converted.append(None)
            elif isinstance(value, Iterable) and not isinstance(value, (str, dict)):
                converted.append(self.to_fhir_types(value))
            elif self.is_fhir_type(value):
                converted.append(value)
            elif self.is_cql_type(value):
                converted.append(self.to_fhir_type(value))
            else:
                raise ValueError(
                    f"Unknown type encountered during conversion: {type(value).__name__}"
                )

        return converted

    def to_fhir_type(self, value: Any) -> Any:
        """Convert a CQL value to FHIR type.

        Args:
            value: CQL value

        Returns:
            FHIR type
        """
        if value is None:
            return None

        if isinstance(value, Iterable) and not isinstance(value, (str, dict)):
            raise ValueError("use to_fhir_types(Iterable) for iterables")

        if self.is_fhir_type(value):
            return value

        if not self.is_cql_type(value):
            raise ValueError(
                f"can't convert {type(value).__name__} to FHIR type"
            )

        type_name = type(value).__name__

        # Map CQL types to FHIR conversions
        if type_name == "bool":
            return self.to_fhir_boolean(value)
        elif type_name == "int":
            return self.to_fhir_integer(value)
        elif type_name == "Decimal":
            return self.to_fhir_decimal(value)
        elif type_name == "Date":
            return self.to_fhir_date(value)
        elif type_name == "DateTime":
            return self.to_fhir_datetime(value)
        elif type_name == "Time":
            return self.to_fhir_time(value)
        elif type_name == "str":
            return self.to_fhir_string(value)
        elif type_name == "Quantity":
            return self.to_fhir_quantity(value)
        elif type_name == "Ratio":
            return self.to_fhir_ratio(value)
        elif type_name == "Any":
            return self.to_fhir_any(value)
        elif type_name == "Code":
            return self.to_fhir_coding(value)
        elif type_name == "Concept":
            return self.to_fhir_codeable_concept(value)
        elif type_name == "Interval":
            return self.to_fhir_interval(value)
        elif type_name == "Tuple":
            return self.to_fhir_tuple(value)
        else:
            raise ValueError(f"missing case statement for: {type_name}")

    def to_fhir_interval(self, value: Any) -> Any:
        """Convert CQL Interval to FHIR Range or Period.

        Args:
            value: CQL Interval

        Returns:
            FHIR Range or Period
        """
        if value is None:
            return None

        # Get point type name
        point_type_name = (
            value.get_point_type().get_type_name()
            if hasattr(value, "get_point_type")
            else str(type(value))
        )
        simple_name = self._get_simple_name(point_type_name)

        if simple_name in ("Date", "DateTime"):
            return self.to_fhir_period(value)
        elif simple_name == "Quantity":
            return self.to_fhir_range(value)
        else:
            raise ValueError(
                f"Unsupported interval point type for FHIR conversion: {point_type_name}"
            )

    def is_cql_type(self, value: Any) -> bool:
        """Check if a value is a CQL type.

        Args:
            value: Value to test

        Returns:
            True if value is a CQL type

        Raises:
            TypeError: If value is None
        """
        if value is None:
            raise TypeError("value cannot be None")

        if isinstance(value, Iterable) and not isinstance(value, (str, dict)):
            raise ValueError("is_cql_type cannot be used for Iterables")

        # CQL types
        cql_type_names = {
            "bool", "int", "str", "float", "Decimal",
            "Date", "DateTime", "Time", "Quantity", "Ratio", "Code", "Concept",
            "Interval", "Tuple"
        }

        type_name = type(value).__name__
        if type_name in cql_type_names:
            return True

        # Check for CQL type classes
        if hasattr(value, "__module__"):
            module = value.__module__
            if "cql_engine" in module or "runtime" in module:
                return True

        return False

    def to_cql_types(self, values: Iterable[Any]) -> Iterable[Any]:
        """Convert FHIR values to CQL types.

        Args:
            values: Iterable of FHIR values

        Returns:
            Iterable of CQL types
        """
        converted = []

        for value in values:
            if value is None:
                converted.append(None)
            elif isinstance(value, Iterable) and not isinstance(value, (str, dict)):
                converted.append(self.to_cql_types(value))
            elif self.is_cql_type(value):
                converted.append(value)
            elif self.is_fhir_type(value):
                converted.append(self.to_cql_type(value))
            else:
                raise ValueError(
                    f"Unknown type encountered during conversion: {type(value).__name__}"
                )

        return converted

    def to_cql_type(self, value: Any) -> Any:
        """Convert a FHIR value to CQL type.

        Args:
            value: FHIR value

        Returns:
            CQL type
        """
        if value is None:
            return None

        if isinstance(value, Iterable) and not isinstance(value, (str, dict)):
            raise ValueError("use to_cql_types(Iterable) for iterables")

        if self.is_cql_type(value):
            return value

        if not self.is_fhir_type(value):
            raise ValueError(
                f"can't convert {type(value).__name__} to CQL type"
            )

        type_name = type(value).__name__

        # Map FHIR types to CQL conversions
        if type_name == "IdType":
            return self.to_cql_id(value)
        elif type_name == "BooleanType":
            return self.to_cql_boolean(value)
        elif type_name == "IntegerType":
            return self.to_cql_integer(value)
        elif type_name == "DecimalType":
            return self.to_cql_decimal(value)
        elif type_name == "DateType":
            return self.to_cql_date(value)
        elif type_name in ("InstantType", "DateTimeType"):
            return self.to_cql_datetime(value)
        elif type_name == "TimeType":
            return self.to_cql_time(value)
        elif type_name == "StringType":
            return self.to_cql_string(value)
        elif type_name == "Quantity":
            return self.to_cql_quantity(value)
        elif type_name == "Ratio":
            return self.to_cql_ratio(value)
        elif type_name == "Coding":
            return self.to_cql_code(value)
        elif type_name == "CodeableConcept":
            return self.to_cql_concept(value)
        elif type_name in ("Period", "Range"):
            return self.to_cql_interval(value)
        else:
            raise ValueError(f"missing case statement for: {type_name}")

    def to_cql_id(self, value: Any) -> Optional[str]:
        """Convert FHIR Id to string.

        Args:
            value: FHIR Id

        Returns:
            String ID
        """
        if value is None:
            return None

        if hasattr(value, "get_id_part"):
            return value.get_id_part()
        if hasattr(value, "id"):
            return value.id
        if isinstance(value, dict):
            return value.get("value")

        return str(value)

    def to_cql_boolean(self, value: Any) -> Optional[bool]:
        """Convert FHIR Boolean to Python bool.

        Args:
            value: FHIR Boolean

        Returns:
            Python bool
        """
        if value is None:
            return None

        if hasattr(value, "get_value"):
            return value.get_value()
        if hasattr(value, "value"):
            return value.value
        if isinstance(value, dict):
            return value.get("value")

        return bool(value)

    def to_cql_integer(self, value: Any) -> Optional[int]:
        """Convert FHIR Integer to Python int.

        Args:
            value: FHIR Integer

        Returns:
            Python int
        """
        if value is None:
            return None

        if hasattr(value, "get_value"):
            return value.get_value()
        if hasattr(value, "value"):
            return value.value
        if isinstance(value, dict):
            return value.get("value")

        return int(value)

    def to_cql_decimal(self, value: Any) -> Optional[Decimal]:
        """Convert FHIR Decimal to Decimal.

        Args:
            value: FHIR Decimal

        Returns:
            Python Decimal
        """
        if value is None:
            return None

        if hasattr(value, "get_value"):
            val = value.get_value()
            return Decimal(str(val)) if val is not None else None
        if hasattr(value, "value"):
            return Decimal(str(value.value)) if value.value is not None else None
        if isinstance(value, dict):
            val = value.get("value")
            return Decimal(str(val)) if val is not None else None

        return Decimal(str(value))

    def to_cql_time(self, value: Any) -> Any:
        """Convert FHIR Time to CQL Time.

        Args:
            value: FHIR Time

        Returns:
            CQL Time
        """
        if value is None:
            return None

        time_str = None
        if hasattr(value, "get_value"):
            time_str = value.get_value()
        elif hasattr(value, "value"):
            time_str = value.value
        elif isinstance(value, dict):
            time_str = value.get("value")
        else:
            time_str = str(value)

        # Import here to avoid circular dependency
        try:
            from cql_engine.runtime import Time
            return Time(time_str) if time_str else None
        except ImportError:
            return time_str

    def to_cql_string(self, value: Any) -> Optional[str]:
        """Convert FHIR String to Python str.

        Args:
            value: FHIR String

        Returns:
            Python str
        """
        if value is None:
            return None

        if hasattr(value, "get_value"):
            return value.get_value()
        if hasattr(value, "value"):
            return value.value
        if isinstance(value, dict):
            return value.get("value")

        return str(value)

    def to_cql_tuple(self, value: Any) -> Any:
        """Convert FHIR Structure to CQL Tuple.

        Args:
            value: FHIR structure

        Returns:
            CQL Tuple

        Raises:
            NotImplementedError: Not yet implemented
        """
        if value is None:
            return None

        raise NotImplementedError("to_cql_tuple is not yet implemented")

    @staticmethod
    def _get_simple_name(type_name: str) -> str:
        """Get the simple name from a qualified type name.

        Args:
            type_name: Qualified type name

        Returns:
            Simple name
        """
        parts = type_name.split(".")
        return parts[-1] if parts else type_name
