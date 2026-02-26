"""
Data Provider Exception

Exception thrown by DataProvider implementations.
"""

from typing import Optional

from .cql_exception import CqlException
from .severity import Severity


class DataProviderException(CqlException):
    """
    Exception thrown by implementations of the DataProvider interface.

    This exception is meant to be raised when data providers encounter
    errors while retrieving or processing data.
    """

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        source_locator: Optional["SourceLocator"] = None,
        severity: Optional[Severity] = None,
    ) -> None:
        """
        Initialize a DataProviderException.

        Args:
            message: The exception message
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
