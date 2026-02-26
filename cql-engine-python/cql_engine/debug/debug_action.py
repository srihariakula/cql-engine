"""
Debug Action Enumeration

Defines debug actions for the CQL engine debugger.
"""

from enum import Enum


class DebugAction(Enum):
    """
    Enumeration of debug actions.

    Specifies what action to take when a debug breakpoint is hit.
    """

    NONE = "NONE"
    LOG = "LOG"
    TRACE = "TRACE"
    WATCH = "WATCH"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"DebugAction.{self.name}"
