"""
Debug Locator Module

Specifies a debug entry point (breakpoint) in CQL code.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .location import Location


class DebugLocatorType(Enum):
    """
    Enumeration of debug locator types.

    Specifies what kind of location a debug locator refers to.
    """

    NODE_ID = "NODE_ID"
    NODE_TYPE = "NODE_TYPE"
    LOCATION = "LOCATION"
    EXCEPTION_TYPE = "EXCEPTION_TYPE"

    def __str__(self) -> str:
        return self.value


@dataclass
class DebugLocator:
    """
    Specifies a debug entry point (breakpoint).

    Can be based on:
    - nodeId: corresponding to the localId element of a node in the ELM
    - nodeType: corresponding to the type of the node (will match all nodes of that type)
    - location: corresponding to a range in the source (will match all nodes with a locator
      range that includes the location)
    - exceptionType: corresponding to the type of an exception (will match whenever an
      exception of this type occurs)
    """

    type: DebugLocatorType
    locator: str
    location: Optional[Location] = None

    def __post_init__(self) -> None:
        """Initialize and validate the debug locator."""
        if self.type == DebugLocatorType.LOCATION:
            return  # location is already set

        self._guard_locator(self.locator)

        if self.type == DebugLocatorType.NODE_TYPE:
            if not self.locator.endswith("Evaluator"):
                object.__setattr__(self, "locator", self.locator + "Evaluator")

    @staticmethod
    def _guard_locator(locator: Optional[str]) -> None:
        """
        Validate that a locator string is not None or empty.

        Args:
            locator: The locator string to validate

        Raises:
            ValueError: If locator is None or empty
        """
        if not locator or not locator.strip():
            raise ValueError("nodeId locator required")

    @classmethod
    def from_location(cls, location: Location) -> "DebugLocator":
        """
        Create a DebugLocator from a Location.

        Args:
            location: The source location

        Returns:
            A DebugLocator with type LOCATION
        """
        locator_str = location.to_locator()
        return cls(type=DebugLocatorType.LOCATION, locator=locator_str, location=location)

    @classmethod
    def from_node_id(cls, node_id: str) -> "DebugLocator":
        """
        Create a DebugLocator from a node ID.

        Args:
            node_id: The node ID

        Returns:
            A DebugLocator with type NODE_ID
        """
        return cls(type=DebugLocatorType.NODE_ID, locator=node_id, location=None)

    @classmethod
    def from_node_type(cls, node_type: str) -> "DebugLocator":
        """
        Create a DebugLocator from a node type.

        Args:
            node_type: The node type

        Returns:
            A DebugLocator with type NODE_TYPE
        """
        return cls(type=DebugLocatorType.NODE_TYPE, locator=node_type, location=None)

    @classmethod
    def from_exception_type(cls, exception_type: str) -> "DebugLocator":
        """
        Create a DebugLocator from an exception type.

        Args:
            exception_type: The exception type name

        Returns:
            A DebugLocator with type EXCEPTION_TYPE
        """
        return cls(type=DebugLocatorType.EXCEPTION_TYPE, locator=exception_type, location=None)

    def get_locator_type(self) -> DebugLocatorType:
        """Get the locator type."""
        return self.type

    def get_locator(self) -> str:
        """Get the locator string."""
        return self.locator

    def get_location(self) -> Optional[Location]:
        """Get the location (for LOCATION type)."""
        return self.location

    def __hash__(self) -> int:
        """Calculate hash based on locator type and string."""
        result = hash(self.locator)
        result = 31 * result + self.type.value.__hash__()
        return result

    def __eq__(self, other: object) -> bool:
        """Check equality based on type and locator."""
        if not isinstance(other, DebugLocator):
            return False
        return self.type == other.type and self.locator == other.locator

    def __str__(self) -> str:
        """Return string representation."""
        return f"DebugLocator(type={self.type}, locator={self.locator})"

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"DebugLocator(type={self.type!r}, locator={self.locator!r}, "
            f"location={self.location!r})"
        )
