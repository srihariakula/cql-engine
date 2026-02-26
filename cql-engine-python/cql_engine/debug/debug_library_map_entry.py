"""
Debug Library Map Entry

Manages debug settings for a single library.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING

from .debug_action import DebugAction
from .debug_locator import DebugLocator, DebugLocatorType
from .debug_map_entry import DebugMapEntry
from .location import Location

if TYPE_CHECKING:
    from cql_engine.elm.execution import Executable


@dataclass
class DebugLibraryMapEntry:
    """
    Manages debug settings for a single library.

    Maintains debug entries (breakpoints) for a specific library,
    organized by node ID and source location.
    """

    library_name: str
    node_entries: Dict[str, DebugMapEntry] = field(default_factory=dict)
    location_entries: Dict[str, DebugMapEntry] = field(default_factory=dict)

    def get_library_name(self) -> str:
        """
        Get the library name.

        Returns:
            The name of the library
        """
        return self.library_name

    def should_debug(self, node: "Executable") -> DebugAction:
        """
        Determine if a node should be debugged.

        Checks if there is a debug entry for this node based on its
        node ID or source location.

        Args:
            node: The node to check

        Returns:
            The debug action to take, or DebugAction.NONE if no debug entry
        """
        # Import here to avoid circular dependency
        try:
            from cql_engine.elm.execution import Element
        except ImportError:
            Element = None

        if Element is not None and isinstance(node, Element):
            # Check by node ID first
            if hasattr(node, "local_id") and node.local_id is not None:
                node_entry = self.node_entries.get(node.local_id)
                if node_entry is not None and node_entry.get_action() != DebugAction.NONE:
                    return node_entry.get_action()

            # Check by location
            if hasattr(node, "locator") and node.locator is not None:
                node_location = Location.from_locator(node.locator)
                for entry in self.location_entries.values():
                    entry_location = entry.get_locator().get_location()
                    if (
                        entry_location is not None
                        and entry_location.includes(node_location)
                        and entry.get_action() != DebugAction.NONE
                    ):
                        return entry.get_action()

        return DebugAction.NONE

    def add_entry(self, debug_locator: DebugLocator, action: DebugAction) -> None:
        """
        Add a debug entry (overload for locator and action).

        Args:
            debug_locator: The debug locator
            action: The debug action
        """
        self.add_entry_from_map_entry(DebugMapEntry(debug_locator, action))

    def add_entry_from_map_entry(self, entry: DebugMapEntry) -> None:
        """
        Add a debug entry from a DebugMapEntry.

        Args:
            entry: The debug map entry to add

        Raises:
            ValueError: If the locator type is not NODE_ID or LOCATION
        """
        locator_type = entry.get_locator().get_locator_type()

        if locator_type == DebugLocatorType.NODE_ID:
            self.node_entries[entry.get_locator().get_locator()] = entry
        elif locator_type == DebugLocatorType.LOCATION:
            self.location_entries[entry.get_locator().get_locator()] = entry
        else:
            raise ValueError(
                "Library debug map entry can only contain node id or location debug entries"
            )

    def remove_entry(self, debug_locator: DebugLocator) -> None:
        """
        Remove a debug entry.

        Args:
            debug_locator: The debug locator to remove

        Raises:
            ValueError: If the locator type is not NODE_ID or LOCATION
        """
        locator_type = debug_locator.get_locator_type()

        if locator_type == DebugLocatorType.NODE_ID:
            self.node_entries.pop(debug_locator.get_locator(), None)
        elif locator_type == DebugLocatorType.LOCATION:
            self.location_entries.pop(debug_locator.get_locator(), None)
        else:
            raise ValueError(
                "Library debug map entry only contains node id or location debug entries"
            )
