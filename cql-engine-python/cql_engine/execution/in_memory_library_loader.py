"""
In-memory library loader for CQL engine.

Provides a library loader that loads from a pre-loaded set of libraries in memory.
"""

from typing import Collection, Dict
from cql_engine.execution.library_loader import LibraryLoader, VersionedIdentifier, Library


class InMemoryLibraryLoader(LibraryLoader):
    """
    LibraryLoader that loads libraries from a pre-loaded in-memory collection.

    Useful for testing and scenarios where all libraries are available in memory
    before evaluation begins.
    """

    def __init__(self, libraries: Collection[Library]):
        """
        Initialize with a collection of libraries.

        Args:
            libraries: Collection of Library objects to load from

        Raises:
            ValueError: If multiple libraries with the same ID are provided
        """
        self.libraries: Dict[str, Library] = {}

        for library in libraries:
            lib_id = library.get_identifier().get_id()
            if lib_id in self.libraries:
                raise ValueError(
                    f"Found multiple versions / instances of library {lib_id}."
                )
            self.libraries[lib_id] = library

    def load(self, library_identifier: VersionedIdentifier) -> Library:
        """
        Load a library from the in-memory collection.

        Args:
            library_identifier: The identifier of the library to load

        Returns:
            The Library with the specified ID

        Raises:
            ValueError: If the library is not found in the collection
        """
        lib_id = library_identifier.get_id()
        library = self.libraries.get(lib_id)
        if library is None:
            raise ValueError(f"Library {lib_id} not found.")
        return library
