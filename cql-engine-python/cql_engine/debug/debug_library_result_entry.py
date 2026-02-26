"""
Debug Library Result Entry

Stores debug results for a single library.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .debug_locator import DebugLocator
from .debug_result_entry import DebugResultEntry
from .location import Location

if TYPE_CHECKING:
    from cql_engine.elm.execution import Executable


@dataclass
class DebugLibraryResultEntry:
    """
    Stores debug results for a single library.

    Maintains a mapping of debug locators to lists of debug result entries
    for nodes evaluated in a particular library.
    """

    library_name: str
    results: Dict[DebugLocator, List[DebugResultEntry]] = field(default_factory=dict)

    def get_library_name(self) -> str:
        """
        Get the library name.

        Returns:
            The name of the library
        """
        return self.library_name

    def get_results(self) -> Dict[DebugLocator, List[DebugResultEntry]]:
        """
        Get all debug results.

        Returns:
            A mapping of debug locators to lists of result entries
        """
        return self.results

    def _log_debug_result(self, locator: DebugLocator, result: Any) -> None:
        """
        Log a debug result for a locator.

        Internal method to log a result at a specific debug locator.

        Args:
            locator: The debug locator
            result: The result value to log
        """
        if locator not in self.results:
            self.results[locator] = []

        self.results[locator].append(DebugResultEntry(result))

    def log_debug_result_entry(self, node: "Executable", result: Any) -> None:
        """
        Log a debug result for a node.

        Creates appropriate DebugLocators based on the node's properties
        (local ID and/or source location) and logs the result.

        Args:
            node: The executed node
            result: The result value to log
        """
        # Import here to avoid circular dependency
        try:
            from cql_engine.elm.execution import Element
        except ImportError:
            Element = None

        if Element is not None and isinstance(node, Element):
            # Node is an Element, use its localId and locator
            if hasattr(node, "local_id") and node.local_id is not None:
                locator = DebugLocator.from_node_id(node.local_id)
                self._log_debug_result(locator, result)

            if hasattr(node, "locator") and node.locator is not None:
                source_location = Location.from_locator(node.locator)
                locator = DebugLocator.from_location(source_location)
                self._log_debug_result(locator, result)
        else:
            # Node is not an Element, use its class name
            node_type = node.__class__.__name__
            locator = DebugLocator.from_node_type(node_type)
            self._log_debug_result(locator, result)
