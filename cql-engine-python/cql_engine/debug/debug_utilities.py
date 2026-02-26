"""
Debug Utilities

Utility functions for debugging CQL execution.
"""

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from cql_engine.elm.execution import Executable, Library


logger = logging.getLogger(__name__)


class DebugUtilities:
    """Utility functions for debugging CQL execution."""

    @staticmethod
    def log_debug_result(node: "Executable", current_library: "Library", result: Any) -> None:
        """
        Log a debug result.

        Args:
            node: The executed node
            current_library: The current library
            result: The result value
        """
        library_id = (
            current_library.identifier.id if current_library else "unknown"
        )
        location = DebugUtilities.to_debug_location(node)
        debug_str = DebugUtilities.to_debug_string(result)
        logger.debug(f"{library_id}.{location}: {debug_str}")

    @staticmethod
    def to_debug_location(node: "Executable") -> str:
        """
        Convert a node to a debug location string.

        Args:
            node: The node

        Returns:
            A string representing the node's location
        """
        result = ""

        try:
            from cql_engine.elm.execution import Element
        except ImportError:
            Element = None

        if Element is not None and isinstance(node, Element):
            if hasattr(node, "locator") and node.locator is not None:
                result = node.locator
            if hasattr(node, "local_id") and node.local_id is not None:
                result += f"({node.local_id})"
        else:
            result = str(type(node))

        return result

    @staticmethod
    def to_debug_string(result: Any) -> str:
        """
        Convert a value to a debug string representation.

        Handles CqlType objects and iterables specially.

        Args:
            result: The value to convert

        Returns:
            A string representation suitable for debugging
        """
        # Check if it's a CqlType
        try:
            from cql_engine.runtime.cql_type import CqlType

            if isinstance(result, CqlType):
                return str(result)
        except ImportError:
            pass

        # Check if it's iterable (but not string)
        if isinstance(result, (list, set, tuple)):
            elements = []
            for element in result:
                elements.append(DebugUtilities.to_debug_string(element))
            return "{" + ",".join(elements) + "}"

        # Null/None check
        if result is None:
            return "<null>"

        # Default to string representation
        return str(result)
