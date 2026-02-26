"""
Debug Map Entry

Maps a debug locator to a debug action.
"""

from dataclasses import dataclass

from .debug_action import DebugAction
from .debug_locator import DebugLocator


@dataclass
class DebugMapEntry:
    """
    Maps a debug locator to a debug action.

    Specifies what action to take when a particular debug point is hit.
    """

    locator: DebugLocator
    action: DebugAction

    def __post_init__(self) -> None:
        """Validate the debug map entry."""
        if self.locator is None:
            raise ValueError("locator required")

    def get_locator(self) -> DebugLocator:
        """
        Get the debug locator.

        Returns:
            The debug locator
        """
        return self.locator

    def get_action(self) -> DebugAction:
        """
        Get the debug action.

        Returns:
            The debug action
        """
        return self.action
