"""
Location Module

Identifies a location in a source file by line and character positions.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Location:
    """
    Represents a location in a source file.

    Identifies a location by starting line and character, and ending line and character.
    """

    start_line: int
    start_char: int
    end_line: int
    end_char: int

    def __hash__(self) -> int:
        """Calculate hash code based on location coordinates."""
        result = 13
        result = 31 * result + self.start_line
        result = 31 * result + self.start_char
        result = 31 * result + self.end_line
        result = 31 * result + self.end_char
        return result

    def __eq__(self, other: object) -> bool:
        """Check if two locations are equal."""
        if not isinstance(other, Location):
            return False
        return (
            self.start_line == other.start_line
            and self.start_char == other.start_char
            and self.end_line == other.end_line
            and self.end_char == other.end_char
        )

    def includes(self, other: "Location") -> bool:
        """
        Check if this location includes another location.

        Returns True if this location starts on or before and ends on or after
        the other location.

        Args:
            other: The location to check

        Returns:
            True if this location includes the other location

        Raises:
            ValueError: If other is None
        """
        if other is None:
            raise ValueError("other required")

        if self.start_line > other.start_line:
            return False

        if self.start_line == other.start_line and self.start_char > other.start_char:
            return False

        if self.end_line < other.end_line:
            return False

        if self.end_line == other.end_line and self.end_char < other.end_char:
            return False

        return True

    def __str__(self) -> str:
        """Return string representation of the location."""
        return (
            f"Location(startLine={self.start_line}, startChar={self.start_char}, "
            f"endLine={self.end_line}, endChar={self.end_char})"
        )

    def to_locator(self) -> str:
        """
        Convert the location to a locator string.

        Format:
        - For point locations: "line:char"
        - For range locations: "startLine:startChar-endLine:endChar"

        Returns:
            The locator string
        """
        if self.start_line == self.end_line and self.start_char == self.end_char:
            return f"{self.start_line}:{self.start_char}"
        else:
            return f"{self.start_line}:{self.start_char}-{self.end_line}:{self.end_char}"

    @staticmethod
    def from_locator(locator: str) -> "Location":
        """
        Parse a location from a locator string.

        Handles formats:
        - Point locations: "line:char" -> Location(line, char, line, char)
        - Range locations: "startLine:startChar-endLine:endChar"

        Args:
            locator: The locator string to parse

        Returns:
            A Location object

        Raises:
            ValueError: If the locator format is invalid
        """
        if not locator or not locator.strip():
            raise ValueError("locator required")

        start_line = 0
        start_char = 0
        end_line = 0
        end_char = 0

        locations = locator.split("-")
        for i, location_str in enumerate(locations):
            ranges = location_str.split(":")
            if len(ranges) != 2:
                raise ValueError(f"Invalid locator format: {locator}")

            try:
                line = int(ranges[0])
                char = int(ranges[1])
            except ValueError:
                raise ValueError(f"Invalid locator format: {locator}")

            if i == 0:
                start_line = line
                start_char = char
            else:
                end_line = line
                end_char = char

        if len(locations) == 1:
            end_line = start_line
            end_char = start_char

        return Location(start_line, start_char, end_line, end_char)
