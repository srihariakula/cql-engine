"""
Debug Map

Manages all debug settings across multiple libraries.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING

from .debug_action import DebugAction
from .debug_locator import DebugLocator, DebugLocatorType
from .debug_library_map_entry import DebugLibraryMapEntry
from .debug_map_entry import DebugMapEntry

if TYPE_CHECKING:
    from cql_engine.elm.execution import Executable, Library


@dataclass
class DebugMap:
    """
    Manages all debug settings across multiple libraries.

    Maintains debug entries for multiple libraries, as well as global
    node type and exception type entries.
    """

    library_maps: Dict[str, DebugLibraryMapEntry] = field(default_factory=dict)
    node_type_entries: Dict[str, DebugMapEntry] = field(default_factory=dict)
    exception_type_entries: Dict[str, DebugMapEntry] = field(default_factory=dict)
    is_logging_enabled: bool = False
    is_coverage_enabled: bool = False

    def should_debug_exception(self, exception: Exception) -> DebugAction:
        """
        Determine what action to take for an exception.

        Args:
            exception: The exception to check

        Returns:
            The debug action to take
        """
        if len(self.exception_type_entries) == 0:
            return DebugAction.LOG
        else:
            exception_type_name = exception.__class__.__name__
            entry = self.exception_type_entries.get(exception_type_name)
            if entry is not None:
                return entry.get_action()

        # Exceptions are always logged unless explicitly disabled
        return DebugAction.LOG

    def should_debug_node(
        self, node: "Executable", current_library: "Library"
    ) -> DebugAction:
        """
        Determine what action to take for a node.

        Checks library-specific, node-type, logging, and coverage settings
        in that order.

        Args:
            node: The node to check
            current_library: The current library

        Returns:
            The debug action to take
        """
        library_id = current_library.identifier.id
        library_map = self.library_maps.get(library_id)

        if library_map is not None:
            action = library_map.should_debug(node)
            if action != DebugAction.NONE:
                return action

        node_type_name = node.__class__.__name__
        node_entry = self.node_type_entries.get(node_type_name)
        if node_entry is not None and node_entry.get_action() != DebugAction.NONE:
            return node_entry.get_action()

        if self.is_logging_enabled:
            return DebugAction.LOG

        if self.is_coverage_enabled:
            return DebugAction.TRACE

        return DebugAction.NONE

    def _get_library_map(self, library_name: str) -> Optional[DebugLibraryMapEntry]:
        """
        Get a library map entry.

        Args:
            library_name: The library name

        Returns:
            The library map entry, or None if not found
        """
        return self.library_maps.get(library_name)

    def _ensure_library_map(self, library_name: str) -> DebugLibraryMapEntry:
        """
        Ensure a library map entry exists, creating it if necessary.

        Args:
            library_name: The library name

        Returns:
            The library map entry
        """
        library_map = self.library_maps.get(library_name)
        if library_map is None:
            library_map = DebugLibraryMapEntry(library_name)
            self.library_maps[library_name] = library_map

        return library_map

    def add_debug_entry(
        self, library_name: Optional[str], debug_locator: DebugLocator, action: DebugAction
    ) -> None:
        """
        Add a debug entry.

        Can optionally be called with just the locator and action for global entries.

        Args:
            library_name: The library name (optional for global entries)
            debug_locator: The debug locator
            action: The debug action

        Raises:
            ValueError: If library_name is required but not provided
        """
        locator_type = debug_locator.get_locator_type()

        if locator_type == DebugLocatorType.NODE_TYPE:
            self.node_type_entries[debug_locator.get_locator()] = DebugMapEntry(
                debug_locator, action
            )
        elif locator_type == DebugLocatorType.EXCEPTION_TYPE:
            self.exception_type_entries[debug_locator.get_locator()] = DebugMapEntry(
                debug_locator, action
            )
        else:
            if library_name is None:
                raise ValueError("Library entries must have a library name specified")

            library_map = self._ensure_library_map(library_name)
            library_map.add_entry(debug_locator, action)

    def add_debug_entry_for_library(
        self, library_name: str, debug_locator: DebugLocator, action: DebugAction
    ) -> None:
        """
        Add a debug entry for a specific library.

        Args:
            library_name: The library name
            debug_locator: The debug locator
            action: The debug action
        """
        self.add_debug_entry(library_name, debug_locator, action)

    def remove_debug_entry(
        self, library_name: Optional[str], debug_locator: DebugLocator
    ) -> None:
        """
        Remove a debug entry.

        Args:
            library_name: The library name (required for library-specific entries)
            debug_locator: The debug locator to remove

        Raises:
            ValueError: If library_name is required but not provided
        """
        locator_type = debug_locator.get_locator_type()

        if locator_type == DebugLocatorType.NODE_TYPE:
            self.node_type_entries.pop(debug_locator.get_locator(), None)
        elif locator_type == DebugLocatorType.EXCEPTION_TYPE:
            self.exception_type_entries.pop(debug_locator.get_locator(), None)
        else:
            if library_name is None:
                raise ValueError("Library entries must have a library name specified")

            library_map = self._get_library_map(library_name)
            if library_map is not None:
                library_map.remove_entry(debug_locator)

    def remove_debug_entry_for_library(
        self, library_name: str, debug_locator: DebugLocator
    ) -> None:
        """
        Remove a debug entry for a specific library.

        Args:
            library_name: The library name
            debug_locator: The debug locator to remove
        """
        self.remove_debug_entry(library_name, debug_locator)

    def get_is_logging_enabled(self) -> bool:
        """
        Check if logging is enabled.

        Returns:
            True if logging is enabled
        """
        return self.is_logging_enabled

    def set_is_logging_enabled(self, enabled: bool) -> None:
        """
        Enable or disable logging.

        Args:
            enabled: True to enable logging
        """
        self.is_logging_enabled = enabled

    def get_is_coverage_enabled(self) -> bool:
        """
        Check if coverage tracing is enabled.

        Returns:
            True if coverage is enabled
        """
        return self.is_coverage_enabled

    def set_is_coverage_enabled(self, enabled: bool) -> None:
        """
        Enable or disable coverage tracing.

        Args:
            enabled: True to enable coverage
        """
        self.is_coverage_enabled = enabled
