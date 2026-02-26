"""FHIR version mismatch exception."""


class FhirVersionMismatchException(RuntimeError):
    """Exception raised when FHIR versions are mismatched across components."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Description of the version mismatch
        """
        super().__init__(message)
