"""DSTU2-specific FHIR type converter."""

from typing import Any, Optional
from decimal import Decimal

from .base_fhir_type_converter import BaseFhirTypeConverter


class Dstu2FhirTypeConverter(BaseFhirTypeConverter):
    """FHIR type converter for DSTU2 (HL7 FHIR version 1.0.2)."""

    # CQL-to-FHIR conversions

    def to_fhir_id(self, value: str) -> Any:
        """Convert string to DSTU2 IdType.

        Args:
            value: String ID

        Returns:
            DSTU2 IdType
        """
        if value is None:
            return None
        # Would need to import DSTU2 types
        return {"value": value}

    def to_fhir_boolean(self, value: Optional[bool]) -> Any:
        """Convert to DSTU2 BooleanType."""
        if value is None:
            return None
        return {"value": value}

    def to_fhir_integer(self, value: Optional[int]) -> Any:
        """Convert to DSTU2 IntegerType."""
        if value is None:
            return None
        return {"value": value}

    def to_fhir_decimal(self, value: Optional[Decimal]) -> Any:
        """Convert to DSTU2 DecimalType."""
        if value is None:
            return None
        return {"value": str(value)}

    def to_fhir_date(self, value: Any) -> Any:
        """Convert CQL Date to DSTU2 DateType."""
        if value is None:
            return None
        return {"value": str(value)}

    def to_fhir_datetime(self, value: Any) -> Any:
        """Convert CQL DateTime to DSTU2 DateTimeType."""
        if value is None:
            return None
        return {"value": str(value)}

    def to_fhir_time(self, value: Any) -> Any:
        """Convert CQL Time to DSTU2 TimeType."""
        if value is None:
            return None
        return {"value": str(value)}

    def to_fhir_string(self, value: Optional[str]) -> Any:
        """Convert to DSTU2 StringType."""
        if value is None:
            return None
        return {"value": value}

    def to_fhir_quantity(self, value: Any) -> Any:
        """Convert CQL Quantity to DSTU2 Quantity."""
        if value is None:
            return None
        return {
            "value": value.get_value() if hasattr(value, "get_value") else value.value,
            "system": "http://unitsofmeasure.org",
            "code": value.get_unit() if hasattr(value, "get_unit") else value.unit,
        }

    def to_fhir_ratio(self, value: Any) -> Any:
        """Convert CQL Ratio to DSTU2 Ratio."""
        if value is None:
            return None
        return {
            "numerator": self.to_fhir_quantity(
                value.get_numerator() if hasattr(value, "get_numerator") else value.numerator
            ),
            "denominator": self.to_fhir_quantity(
                value.get_denominator() if hasattr(value, "get_denominator") else value.denominator
            ),
        }

    def to_fhir_any(self, value: Any) -> Any:
        """Convert CQL Any."""
        if value is None:
            return None
        raise NotImplementedError("Unable to convert System.Any types")

    def to_fhir_coding(self, value: Any) -> Any:
        """Convert CQL Code to DSTU2 Coding."""
        if value is None:
            return None
        return {
            "system": value.get_system() if hasattr(value, "get_system") else value.system,
            "code": value.get_code() if hasattr(value, "get_code") else value.code,
            "display": value.get_display() if hasattr(value, "get_display") else value.display,
            "version": value.get_version() if hasattr(value, "get_version") else value.version,
        }

    def to_fhir_codeable_concept(self, value: Any) -> Any:
        """Convert CQL Concept to DSTU2 CodeableConcept."""
        if value is None:
            return None

        concept = {
            "text": value.get_display() if hasattr(value, "get_display") else value.display,
            "coding": [],
        }

        codes = value.get_codes() if hasattr(value, "get_codes") else value.codes
        if codes:
            for code in codes:
                concept["coding"].append(self.to_fhir_coding(code))

        return concept

    def to_fhir_period(self, value: Any) -> Any:
        """Convert CQL Interval to DSTU2 Period."""
        if value is None:
            return None

        period = {}
        if hasattr(value, "get_low"):
            low = value.get_low()
        else:
            low = value.low if hasattr(value, "low") else None

        if low:
            period["start"] = str(low)

        if hasattr(value, "get_high"):
            high = value.get_high()
        else:
            high = value.high if hasattr(value, "high") else None

        if high:
            period["end"] = str(high)

        return period

    def to_fhir_range(self, value: Any) -> Any:
        """Convert CQL Interval to DSTU2 Range."""
        if value is None:
            return None

        range_obj = {}

        if hasattr(value, "get_low"):
            low = value.get_low()
        else:
            low = value.low if hasattr(value, "low") else None

        if low:
            range_obj["low"] = self.to_fhir_quantity(low)

        if hasattr(value, "get_high"):
            high = value.get_high()
        else:
            high = value.high if hasattr(value, "high") else None

        if high:
            range_obj["high"] = self.to_fhir_quantity(high)

        return range_obj

    def to_fhir_tuple(self, value: Any) -> Any:
        """Convert CQL Tuple to FHIR Structure."""
        if value is None:
            return None
        raise NotImplementedError("to_fhir_tuple is not yet implemented")

    # FHIR-to-CQL conversions

    def to_cql_date(self, value: Any) -> Any:
        """Convert DSTU2 DateType to CQL Date."""
        if value is None:
            return None
        try:
            from cql_engine.runtime import Date
            return Date(str(value))
        except ImportError:
            return str(value)

    def to_cql_datetime(self, value: Any) -> Any:
        """Convert DSTU2 DateTimeType to CQL DateTime."""
        if value is None:
            return None
        try:
            from cql_engine.runtime import DateTime
            return DateTime(str(value))
        except ImportError:
            return str(value)

    def to_cql_temporal(self, value: Any) -> Any:
        """Convert DSTU2 temporal to CQL BaseTemporal."""
        if value is None:
            return None
        type_name = type(value).__name__
        if type_name == "DateType":
            return self.to_cql_date(value)
        elif type_name in ("DateTimeType", "InstantType"):
            return self.to_cql_datetime(value)
        else:
            raise ValueError(f"Not a temporal type: {type_name}")

    def to_cql_quantity(self, value: Any) -> Any:
        """Convert DSTU2 Quantity to CQL Quantity."""
        if value is None:
            return None
        try:
            from cql_engine.runtime import Quantity
            val = value.get("value") if isinstance(value, dict) else getattr(value, "value", None)
            unit = value.get("code") if isinstance(value, dict) else getattr(value, "code", None)
            system = value.get("system") if isinstance(value, dict) else getattr(value, "system", None)
            return Quantity(value=val, unit=unit)
        except ImportError:
            return value

    def to_cql_ratio(self, value: Any) -> Any:
        """Convert DSTU2 Ratio to CQL Ratio."""
        if value is None:
            return None
        try:
            from cql_engine.runtime import Ratio
            numerator = value.get("numerator") if isinstance(value, dict) else getattr(value, "numerator", None)
            denominator = value.get("denominator") if isinstance(value, dict) else getattr(value, "denominator", None)
            return Ratio(
                numerator=self.to_cql_quantity(numerator),
                denominator=self.to_cql_quantity(denominator),
            )
        except ImportError:
            return value

    def to_cql_code(self, value: Any) -> Any:
        """Convert DSTU2 Coding to CQL Code."""
        if value is None:
            return None
        try:
            from cql_engine.runtime import Code
            system = value.get("system") if isinstance(value, dict) else getattr(value, "system", None)
            code = value.get("code") if isinstance(value, dict) else getattr(value, "code", None)
            display = value.get("display") if isinstance(value, dict) else getattr(value, "display", None)
            version = value.get("version") if isinstance(value, dict) else getattr(value, "version", None)
            return Code(system=system, code=code, display=display, version=version)
        except ImportError:
            return value

    def to_cql_concept(self, value: Any) -> Any:
        """Convert DSTU2 CodeableConcept to CQL Concept."""
        if value is None:
            return None
        try:
            from cql_engine.runtime import Concept
            display = value.get("text") if isinstance(value, dict) else getattr(value, "text", None)
            codings = value.get("coding", []) if isinstance(value, dict) else getattr(value, "coding", [])
            codes = [self.to_cql_code(c) for c in codings]
            return Concept(codes=codes, display=display)
        except ImportError:
            return value

    def to_cql_interval(self, value: Any) -> Any:
        """Convert DSTU2 Period or Range to CQL Interval."""
        if value is None:
            return None
        try:
            from cql_engine.runtime import Interval
            type_name = type(value).__name__
            if isinstance(value, dict):
                type_name = "Period" if "start" in value else "Range"

            if type_name == "Period" or "start" in (value if isinstance(value, dict) else {}):
                low = value.get("start") if isinstance(value, dict) else getattr(value, "start", None)
                high = value.get("end") if isinstance(value, dict) else getattr(value, "end", None)
                return Interval(low=low, high=high)
            else:
                low = value.get("low") if isinstance(value, dict) else getattr(value, "low", None)
                high = value.get("high") if isinstance(value, dict) else getattr(value, "high", None)
                low_qty = self.to_cql_quantity(low) if low else None
                high_qty = self.to_cql_quantity(high) if high else None
                return Interval(low=low_qty, high=high_qty)
        except ImportError:
            return value
