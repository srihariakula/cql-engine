"""R4-specific FHIR model resolver."""

from typing import Any

from .fhir_model_resolver import FhirModelResolver


class R4FhirModelResolver(FhirModelResolver):
    """FHIR model resolver for R4 (HL7 FHIR version 4.0.1)."""

    def __init__(self, fhir_context: Any = None) -> None:
        """Initialize R4 model resolver.

        Args:
            fhir_context: FHIR context for R4
        """
        super().__init__(fhir_context)

    def initialize(self) -> None:
        """Initialize R4-specific type handling."""
        self.set_package_names(["org.hl7.fhir.r4.model"])

    def _equals_deep(self, left: Any, right: Any) -> bool:
        """Deep equality comparison for R4 types.

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

        # For R4, would use equalsDeep method if available
        if hasattr(left, "equals_deep"):
            return left.equals_deep(right)

        # Fallback to simple equality
        return left == right
