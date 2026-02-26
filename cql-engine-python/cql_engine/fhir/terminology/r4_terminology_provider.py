"""R4 FHIR terminology provider."""

from typing import Any, Optional
from abc import ABC


class R4FhirTerminologyProvider(ABC):
    """FHIR terminology provider for R4.

    Interfaces with a FHIR server to expand value sets, validate codes,
    and translate codes.
    """

    def __init__(self, base_url: Optional[str] = None) -> None:
        """Initialize the terminology provider.

        Args:
            base_url: Base URL of FHIR terminology server
        """
        self.base_url = base_url

    def expand(self, value_set_info: Any) -> list:
        """Expand a value set.

        Args:
            value_set_info: ValueSet information with ID and other details

        Returns:
            List of codes in the value set

        Raises:
            NotImplementedError: If FHIR library not available
        """
        raise NotImplementedError(
            "Expansion requires fhirclient or similar FHIR library integration"
        )

    def validate_code(self, code_system: str, code: str, display: Optional[str] = None) -> bool:
        """Validate that a code exists in a code system.

        Args:
            code_system: Code system URL
            code: Code to validate
            display: Optional display text

        Returns:
            True if code is valid

        Raises:
            NotImplementedError: If FHIR library not available
        """
        raise NotImplementedError(
            "Validation requires fhirclient or similar FHIR library integration"
        )

    def translate(self, code: str, code_system: str, target_code_system: str) -> Optional[str]:
        """Translate a code from one system to another.

        Args:
            code: Code to translate
            code_system: Source code system
            target_code_system: Target code system

        Returns:
            Translated code, or None if not found

        Raises:
            NotImplementedError: If FHIR library not available
        """
        raise NotImplementedError(
            "Translation requires fhirclient or similar FHIR library integration"
        )
