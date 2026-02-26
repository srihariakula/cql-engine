"""CQL ValueSet type."""

from dataclasses import dataclass, field
from typing import Optional, Iterable

from .vocabulary import Vocabulary
from .code_system import CodeSystem


@dataclass
class ValueSet(Vocabulary):
    """Represents a value set containing multiple code systems.

    A value set is a collection of code systems.
    """

    code_systems: list[CodeSystem] = field(default_factory=list)

    def with_id(self, id: str) -> "ValueSet":
        """Set the value set ID.

        Args:
            id: The value set ID

        Returns:
            Self for method chaining
        """
        self.set_id(id)
        return self

    def with_version(self, version: str) -> "ValueSet":
        """Set the value set version.

        Args:
            version: The value set version

        Returns:
            Self for method chaining
        """
        self.set_version(version)
        return self

    def with_name(self, name: str) -> "ValueSet":
        """Set the value set name.

        Args:
            name: The value set name

        Returns:
            Self for method chaining
        """
        self.set_name(name)
        return self

    def set_code_systems(self, code_systems: Optional[Iterable[CodeSystem]]) -> None:
        """Set the code systems.

        Args:
            code_systems: The code systems for this value set
        """
        self.code_systems.clear()
        if code_systems:
            for cs in code_systems:
                if cs is not None:
                    self.add_code_system(cs)

    def with_code_systems(self, code_systems: Iterable[CodeSystem]) -> "ValueSet":
        """Set the code systems.

        Args:
            code_systems: The code systems for this value set

        Returns:
            Self for method chaining
        """
        self.set_code_systems(code_systems)
        return self

    def add_code_system(self, code_system: CodeSystem) -> None:
        """Add a code system to this value set.

        Args:
            code_system: The code system to add

        Raises:
            ValueError: If code_system is None
        """
        if code_system is None:
            raise ValueError("code_system is required")
        self.code_systems.append(code_system)

    def with_code_system(self, code_system: CodeSystem) -> "ValueSet":
        """Add a code system to this value set.

        Args:
            code_system: The code system to add

        Returns:
            Self for method chaining
        """
        self.add_code_system(code_system)
        return self

    def get_code_system(self, id: str, version: Optional[str] = None) -> Optional[CodeSystem]:
        """Get a code system by ID and optional version.

        Args:
            id: The code system ID
            version: Optional code system version

        Returns:
            The matching CodeSystem, or None if not found
        """
        if id is None:
            return None

        for cs in self.code_systems:
            if cs.id == id:
                if version is None:
                    if cs.version is None:
                        return cs
                elif cs.version == version:
                    return cs

        return None

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if equivalent
        """
        if not isinstance(other, ValueSet):
            return False

        if not super().equivalent(other):
            return False

        if len(self.code_systems) != len(other.code_systems):
            return False

        for cs in self.code_systems:
            other_cs = other.get_code_system(cs.id)
            if other_cs is None:
                return False

        return True

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if equal, False if not, None if uncertain
        """
        if not isinstance(other, ValueSet):
            return False

        if not super().equal(other):
            return False

        if len(self.code_systems) != len(other.code_systems):
            return False

        for cs in self.code_systems:
            other_cs = other.get_code_system(cs.id, cs.version)
            if other_cs is None:
                return False

        return True

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((self.id, self.version, self.name, tuple(self.code_systems)))
