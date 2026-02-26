"""CQL Vocabulary base class."""

from dataclasses import dataclass, field
from typing import Optional

from .cql_type import CqlType


@dataclass
class Vocabulary(CqlType):
    """Base class for vocabulary types (CodeSystem, ValueSet)."""

    id: Optional[str] = None
    version: Optional[str] = None
    name: Optional[str] = None

    def set_id(self, id: str) -> None:
        """Set the vocabulary ID."""
        self.id = id

    def set_version(self, version: str) -> None:
        """Set the vocabulary version."""
        self.version = version

    def set_name(self, name: str) -> None:
        """Set the vocabulary name."""
        self.name = name

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if version is equivalent
        """
        if not isinstance(other, Vocabulary):
            return False
        return self.version == other.version

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if id and version are equal, False if not, None if uncertain
        """
        if not isinstance(other, Vocabulary):
            return False

        id_equal = (self.id is None and other.id is None) or (self.id == other.id)
        version_equal = (self.version is None and other.version is None) or (
            self.version == other.version
        )

        return id_equal and version_equal

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Vocabulary):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((self.id, self.version, self.name))
