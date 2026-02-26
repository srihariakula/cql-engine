"""
CQL Engine Exception Severity Enumeration

Defines severity levels for CQL exceptions.
"""

from enum import Enum


class Severity(Enum):
    """Enumeration of exception severity levels."""

    MESSAGE = "MESSAGE"
    WARNING = "WARNING"
    TRACE = "TRACE"
    ERROR = "ERROR"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Severity.{self.name}"
