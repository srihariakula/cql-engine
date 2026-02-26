"""Version integrity checker for FHIR."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class FhirVersionEnum(Enum):
    """FHIR version enumeration."""

    DSTU2 = "DSTU2"
    DSTU3 = "DSTU3"
    R4 = "R4"
    R5 = "R5"


class FhirVersionIntegrityChecker(ABC):
    """Interface for checking FHIR version integrity across components."""

    @abstractmethod
    def validate_fhir_version_integrity(
        self, fhir_version_enum: FhirVersionEnum
    ) -> None:
        """Validate that all components use the same FHIR version.

        Args:
            fhir_version_enum: The FHIR version to validate

        Raises:
            FhirVersionMismatchException: If versions don't match
        """
        pass

    @staticmethod
    def fetch_fhir_version_enum(fhir_context: Optional[object]) -> FhirVersionEnum:
        """Get the FHIR version from a context.

        Args:
            fhir_context: FHIR context object

        Returns:
            The FHIR version

        Raises:
            ValueError: If context is None or version cannot be determined
        """
        if fhir_context is None:
            raise ValueError("The provided argument is null")

        # Try to extract version from context
        try:
            if hasattr(fhir_context, "get_version"):
                version = fhir_context.get_version()
                if hasattr(version, "get_version"):
                    version_str = version.get_version()
                    if hasattr(version_str, "value"):
                        version_str = version_str.value

                    version_str = str(version_str).upper()
                    return FhirVersionEnum[version_str]
        except (KeyError, AttributeError, ValueError):
            pass

        raise ValueError("Could not determine FHIR version from context")
