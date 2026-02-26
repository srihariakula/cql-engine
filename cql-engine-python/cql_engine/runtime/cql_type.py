"""CQL Type Protocol - Base type for all CQL runtime types."""

from typing import Any, Protocol


class CqlType(Protocol):
    """Protocol for all CQL runtime types.

    Defines the interface that all CQL types must implement for equality
    and equivalence operations.
    """

    def equivalent(self, other: Any) -> bool:
        """Check equivalence with another value.

        Equivalence is less strict than equality and may ignore
        things like version information.

        Args:
            other: The value to compare against

        Returns:
            True if equivalent, False otherwise
        """
        ...

    def equal(self, other: Any) -> bool | None:
        """Check equality with another value.

        Equality is strict and requires all properties to match.

        Args:
            other: The value to compare against

        Returns:
            True if equal, False if not equal, None if uncertain
        """
        ...
