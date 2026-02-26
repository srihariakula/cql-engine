"""DSTU2-specific FHIR model resolver."""

from typing import Any, List

from .fhir_model_resolver import FhirModelResolver


class Dstu2FhirModelResolver(FhirModelResolver):
    """FHIR model resolver for DSTU2 (HL7 FHIR version 1.0.2)."""

    def __init__(self, fhir_context: Any = None) -> None:
        """Initialize DSTU2 model resolver.

        Args:
            fhir_context: FHIR context for DSTU2
        """
        # If no context provided, would need to create one
        # This requires fhirclient or similar library
        super().__init__(fhir_context)

    def initialize(self) -> None:
        """Initialize DSTU2-specific type handling."""
        self.set_package_names(["org.hl7.fhir.dstu2.model"])

    def _equals_deep(self, left: Any, right: Any) -> bool:
        """Deep equality comparison for DSTU2 types.

        Args:
            left: First value
            right: Second value

        Returns:
            True if equal
        """
        if left is right:
            return True

        if type(left) != type(right):
            return False

        # For DSTU2, would use equalsDeep method if available
        if hasattr(left, "equals_deep"):
            return left.equals_deep(right)

        # Fallback to simple equality
        return left == right
