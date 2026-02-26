"""
Source Locator Module

Provides location information for nodes in CQL source code.
"""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from .location import Location

if TYPE_CHECKING:
    from cql_engine.elm.execution import Executable


@dataclass
class SourceLocator:
    """
    Locates a node in a CQL source file.

    Provides information about where a node appears in the source code,
    including library identifier, node ID, and source location.
    """

    library_system_id: str
    library_name: str
    library_version: Optional[str]
    node_id: Optional[str]
    node_type: str
    source_location: Optional[Location]

    def get_library_system_id(self) -> str:
        """Get the library system identifier."""
        return self.library_system_id

    def get_library_name(self) -> str:
        """Get the library name."""
        return self.library_name

    def get_library_version(self) -> Optional[str]:
        """Get the library version."""
        return self.library_version

    def get_node_id(self) -> Optional[str]:
        """Get the node ID."""
        return self.node_id

    def get_node_type(self) -> str:
        """Get the node type."""
        return self.node_type

    def get_source_location(self) -> Optional[Location]:
        """Get the source location."""
        return self.source_location

    @staticmethod
    def strip_evaluator(node_type: Optional[str]) -> Optional[str]:
        """
        Strip the 'Evaluator' suffix from a node type name.

        Args:
            node_type: The node type name

        Returns:
            The node type with 'Evaluator' suffix removed, if present
        """
        if node_type is None:
            return node_type

        if node_type.endswith("Evaluator"):
            return node_type[: -len("Evaluator")]

        return node_type

    def _get_location(self) -> str:
        """
        Get the location string for this source locator.

        Format: "<source_location>(<node_id_or_type>)"

        Returns:
            The location string
        """
        location_str = (
            self.source_location.to_locator() if self.source_location else "?"
        )

        id_or_type = None
        if self.node_id is not None:
            id_or_type = self.node_id
        elif self.node_type is not None:
            id_or_type = self.node_type
        else:
            id_or_type = "?"

        return f"{location_str}({id_or_type})"

    def __str__(self) -> str:
        """Return string representation of the source locator."""
        location = self._get_location()
        library_name = self.library_name if self.library_name else "?"
        return f"{library_name}.{location}"

    def __repr__(self) -> str:
        """Return detailed representation of the source locator."""
        return (
            f"SourceLocator(library_system_id={self.library_system_id!r}, "
            f"library_name={self.library_name!r}, "
            f"library_version={self.library_version!r}, "
            f"node_id={self.node_id!r}, "
            f"node_type={self.node_type!r}, "
            f"source_location={self.source_location!r})"
        )
