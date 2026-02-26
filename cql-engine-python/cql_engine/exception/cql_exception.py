"""
CQL Engine Base Exception

Core exception class for all CQL engine exceptions.
"""

from typing import Optional, TYPE_CHECKING

from .severity import Severity

if TYPE_CHECKING:
    from cql_engine.debug.source_locator import SourceLocator


class CqlException(Exception):
    """
    Base exception for the CQL engine.

    This exception can contain a severity level and source location information
    for debugging purposes.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        cause: Optional[Exception] = None,
        source_locator: Optional["SourceLocator"] = None,
        severity: Optional[Severity] = None,
    ) -> None:
        """
        Initialize a CqlException.

        Args:
            message: The exception message
            cause: The underlying exception that caused this exception
            source_locator: The source location where the exception occurred
            severity: The severity level of the exception (defaults to ERROR)
        """
        # If no message provided but we have a cause, use the cause's message
        if message is None and cause is not None:
            message = str(cause)

        super().__init__(message)
        self.__cause__ = cause
        self.source_locator = source_locator
        self.severity = severity if severity is not None else Severity.ERROR

    def get_severity(self) -> Severity:
        """
        Get the severity level of this exception.

        Returns:
            The severity level
        """
        return self.severity

    def get_source_locator(self) -> Optional["SourceLocator"]:
        """
        Get the source location where this exception occurred.

        Returns:
            The source locator, or None if not set
        """
        return self.source_locator

    def set_source_locator(self, source_locator: Optional["SourceLocator"]) -> None:
        """
        Set the source location where this exception occurred.

        Args:
            source_locator: The source locator to set
        """
        self.source_locator = source_locator

    def __str__(self) -> str:
        message = super().__str__()
        severity_str = f" [{self.severity.value}]" if self.severity else ""
        return f"{message}{severity_str}"

    def __repr__(self) -> str:
        return (
            f"CqlException(message={super().__str__()!r}, "
            f"severity={self.severity}, "
            f"source_locator={self.source_locator!r})"
        )
