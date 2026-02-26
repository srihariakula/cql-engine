"""CQL Code type."""

from dataclasses import dataclass, field
from typing import Optional

from .cql_type import CqlType


@dataclass
class Code(CqlType):
    """Represents a coded concept with code, system, and display values."""

    code: Optional[str] = None
    display: Optional[str] = None
    system: Optional[str] = None
    version: Optional[str] = None

    def with_code(self, code: str) -> "Code":
        """Set the code.

        Args:
            code: The code value

        Returns:
            Self for method chaining
        """
        self.code = code
        return self

    def with_display(self, display: str) -> "Code":
        """Set the display value.

        Args:
            display: The display text

        Returns:
            Self for method chaining
        """
        self.display = display
        return self

    def with_system(self, system: str) -> "Code":
        """Set the code system.

        Args:
            system: The code system identifier

        Returns:
            Self for method chaining
        """
        self.system = system
        return self

    def with_version(self, version: str) -> "Code":
        """Set the version.

        Args:
            version: The code system version

        Returns:
            Self for method chaining
        """
        self.version = version
        return self

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if code and system are equivalent
        """
        if not isinstance(other, Code):
            return False
        return self.code == other.code and self.system == other.system

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if all properties are equal, False if not, None if uncertain
        """
        if not isinstance(other, Code):
            return False

        code_equal = self.code == other.code
        system_equal = self.system == other.system
        version_equal = self.version == other.version
        display_equal = self.display == other.display

        # Handle None cases
        if code_equal is False:
            code_equal = self.code is None and other.code is None
        if system_equal is False:
            system_equal = self.system is None and other.system is None
        if version_equal is False:
            version_equal = self.version is None and other.version is None
        if display_equal is False:
            display_equal = self.display is None and other.display is None

        if not code_equal or not system_equal or not version_equal or not display_equal:
            return None if any([not x for x in [code_equal, system_equal, version_equal, display_equal]]) else False

        return code_equal and system_equal and version_equal and display_equal

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Code):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((self.code, self.system, self.version, self.display))

    def __str__(self) -> str:
        """Get string representation."""
        return f"Code {{ code: {self.code}, system: {self.system}, version: {self.version}, display: {self.display} }}"
