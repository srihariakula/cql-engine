"""
Debug Result

Aggregates debug results and messages for execution.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .debug_action import DebugAction
from .debug_library_result_entry import DebugLibraryResultEntry
from .debug_utilities import DebugUtilities

if TYPE_CHECKING:
    from cql_engine.elm.execution import Executable, Library
    from cql_engine.exception import CqlException


@dataclass
class DebugResult:
    """
    Aggregates debug results and messages for execution.

    Maintains debug results for all libraries and collects error messages
    that occurred during execution.
    """

    library_results: Dict[str, DebugLibraryResultEntry] = field(default_factory=dict)
    messages: List["CqlException"] = field(default_factory=list)

    def log_debug_result(
        self, node: "Executable", current_library: "Library", result: Any, action: DebugAction
    ) -> None:
        """
        Log a debug result for a node.

        Args:
            node: The executed node
            current_library: The current library context
            result: The result value
            action: The debug action that triggered this log
        """
        try:
            library_id = current_library.identifier.id
            library_result_entry = self.library_results.get(library_id)

            if library_result_entry is None:
                library_result_entry = DebugLibraryResultEntry(library_id)
                self.library_results[library_result_entry.get_library_name()] = (
                    library_result_entry
                )

            if library_result_entry is not None:
                library_result_entry.log_debug_result_entry(node, result)

            if action == DebugAction.LOG:
                DebugUtilities.log_debug_result(node, current_library, result)
        except Exception:
            # Do nothing - an exception logging debug helps no one
            pass

    def log_debug_error(self, exception: "CqlException") -> None:
        """
        Log a debug error message.

        Args:
            exception: The CQL exception to log
        """
        self.messages.append(exception)

    def get_messages(self) -> List["CqlException"]:
        """
        Get all error messages.

        Returns:
            List of CQL exceptions that occurred during execution
        """
        return self.messages

    def get_library_results(self) -> Dict[str, DebugLibraryResultEntry]:
        """
        Get all library debug results.

        Returns:
            Mapping of library names to their debug result entries
        """
        return self.library_results
