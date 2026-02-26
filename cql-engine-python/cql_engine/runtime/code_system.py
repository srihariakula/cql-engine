"""CQL CodeSystem type."""

from typing import Optional

from .vocabulary import Vocabulary


class CodeSystem(Vocabulary):
    """Represents a code system in CQL.

    A code system is a collection of codes with associated meanings.
    """

    def with_id(self, id: str) -> "CodeSystem":
        """Set the code system ID.

        Args:
            id: The code system ID

        Returns:
            Self for method chaining
        """
        self.set_id(id)
        return self

    def with_version(self, version: str) -> "CodeSystem":
        """Set the code system version.

        Args:
            version: The code system version

        Returns:
            Self for method chaining
        """
        self.set_version(version)
        return self

    def with_name(self, name: str) -> "CodeSystem":
        """Set the code system name.

        Args:
            name: The code system name

        Returns:
            Self for method chaining
        """
        self.set_name(name)
        return self

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if equivalent
        """
        if not isinstance(other, CodeSystem):
            return False
        return super().equivalent(other)

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if equal, False if not, None if uncertain
        """
        if not isinstance(other, CodeSystem):
            return False
        return super().equal(other)
