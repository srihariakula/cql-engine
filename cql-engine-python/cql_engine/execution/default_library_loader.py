"""
Default library loader implementation for CQL engine.

Provides a default (non-functional) library loader that throws an error.
"""

from cql_engine.execution.library_loader import LibraryLoader, VersionedIdentifier, Library


class CqlException(Exception):
    """Exception raised during CQL execution."""
    pass


class DefaultLibraryLoader(LibraryLoader):
    """
    Default implementation of LibraryLoader.

    This is a placeholder implementation that always throws an exception,
    indicating that library loading is not implemented. Actual implementations
    should override this to provide real library loading functionality.
    """

    def load(self, library_identifier: VersionedIdentifier) -> Library:
        """
        Load a library.

        This default implementation always throws an exception.

        Args:
            library_identifier: The library identifier

        Returns:
            Never returns - always raises an exception

        Raises:
            CqlException: Always raised to indicate loading is not implemented
        """
        raise CqlException("Library loader is not implemented.")
