"""CQL Concept type."""

from dataclasses import dataclass, field
from typing import Optional, Iterable

from .cql_type import CqlType
from .code import Code


@dataclass
class Concept(CqlType):
    """Represents a concept which contains one or more codes.

    A concept is a grouping of related codes.
    """

    codes: list[Code] = field(default_factory=list)
    display: Optional[str] = None

    def with_display(self, display: str) -> "Concept":
        """Set the display value.

        Args:
            display: The display text

        Returns:
            Self for method chaining
        """
        self.display = display
        return self

    def set_codes(self, codes: Optional[Iterable[Code]]) -> None:
        """Set the codes.

        Args:
            codes: The codes for this concept
        """
        self.codes.clear()
        if codes:
            self.codes.extend(codes)

    def with_codes(self, codes: Iterable[Code]) -> "Concept":
        """Set the codes.

        Args:
            codes: The codes for this concept

        Returns:
            Self for method chaining
        """
        self.set_codes(codes)
        return self

    def with_code(self, code: Code) -> "Concept":
        """Add a code to this concept.

        Args:
            code: The code to add

        Returns:
            Self for method chaining
        """
        self.codes.append(code)
        return self

    def equivalent(self, other: object) -> bool:
        """Check equivalence.

        Args:
            other: The other value

        Returns:
            True if at least one code is equivalent
        """
        if not isinstance(other, Concept):
            return False

        if not self.codes or not other.codes:
            return False

        for code in self.codes:
            for other_code in other.codes:
                if code.equivalent(other_code):
                    return True

        return False

    def equal(self, other: object) -> Optional[bool]:
        """Check equality.

        Args:
            other: The other value

        Returns:
            True if equal, False if not, None if uncertain
        """
        if not isinstance(other, Concept):
            return False

        codes_equal = self.codes == other.codes
        display_equal = self.display == other.display

        if not codes_equal and not (not self.codes and not other.codes):
            return False

        if display_equal is False:
            display_equal = self.display is None and other.display is None

        return codes_equal and display_equal

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Concept):
            return False
        return self.equivalent(other)

    def __hash__(self) -> int:
        """Get hash code."""
        return hash((tuple(self.codes), self.display))

    def __str__(self) -> str:
        """Get string representation."""
        lines = ["Concept {"]
        for code in self.codes:
            lines.append(f"\t{code}")
        lines.append("}")
        return "\n".join(lines)
