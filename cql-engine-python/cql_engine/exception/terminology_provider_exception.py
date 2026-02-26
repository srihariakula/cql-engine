"""
Terminology Provider Exception

Exception thrown by TerminologyProvider implementations.
"""

from typing import Optional

from .cql_exception import CqlException
from .severity import Severity


class TerminologyProviderException(CqlException):
    """
    Exception thrown by implementations of the TerminologyProvider interface.

    This exception is meant to be raised when terminology providers encounter
    errors while retrieving or processing terminology data.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        cause: Optional[Exception] = None,
        source_locator: Optional["SourceLocator"] = None,
        severity: Optional[Severity] = None,
    ) -> None:
        """
        Initialize a TerminologyProviderException.

        Args:
            message: The exception message (optional if cause provided)
            cause: The underlying exception (optional)
            source_locator: The source location (optional)
            severity: The severity level (optional)
        """
        super().__init__(
            message=message,
            cause=cause,
            source_locator=source_locator,
            severity=severity,
        )
