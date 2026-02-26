"""Factory for creating FHIR type converters."""

from .dstu2_type_converter import Dstu2FhirTypeConverter
from .dstu3_type_converter import Dstu3FhirTypeConverter
from .r4_type_converter import R4FhirTypeConverter
from .r5_type_converter import R5FhirTypeConverter
from .fhir_type_converter import FhirTypeConverter


class FhirTypeConverterFactory:
    """Factory for creating FHIR type converters."""

    @staticmethod
    def create_converter(fhir_version: str) -> FhirTypeConverter:
        """Create a FHIR type converter for the given version.

        Args:
            fhir_version: FHIR version string (DSTU2, DSTU3, R4, R5)

        Returns:
            Appropriate type converter

        Raises:
            ValueError: If version is not supported
        """
        version_upper = str(fhir_version).upper()

        if version_upper in ("DSTU2", "1.0.2"):
            return Dstu2FhirTypeConverter()
        elif version_upper in ("DSTU3", "3.0.1", "3.0.0"):
            return Dstu3FhirTypeConverter()
        elif version_upper in ("R4", "4.0.1", "4.0.0"):
            return R4FhirTypeConverter()
        elif version_upper in ("R5", "5.0.0"):
            return R5FhirTypeConverter()
        else:
            raise ValueError(f"Unsupported FHIR version: {fhir_version}")
