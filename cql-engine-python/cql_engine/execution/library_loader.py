"""
Library loader interface for CQL engine.

Provides abstraction for loading CQL/ELM libraries.
"""

from abc import ABC, abstractmethod


class VersionedIdentifier:
    """Placeholder - ELM VersionedIdentifier type."""
    pass


class Library:
    """Placeholder - ELM Library type."""
    pass


class LibraryLoader(ABC):
    """
    Interface for loading CQL/ELM libraries.

    Implementations handle loading libraries from various sources
    during CQL evaluation.
    """

    @abstractmethod
    def load(self, library_identifier: VersionedIdentifier) -> Library:
        """
        Load a library by its identifier.

        Args:
            library_identifier: The versioned identifier of the library to load

        Returns:
            The loaded Library

        Raises:
            ValueError: If the library cannot be found or loaded
        """
        pass
