"""
Library wrapper for CQL engine.

Simple wrapper for ELM Library objects.
"""

from typing import Optional, Any


class LibraryWrapper:
    """
    A simple wrapper around a CQL Library object.

    This wrapper provides getter/setter access to a Library, allowing for
    encapsulation and potential future enhancement of Library access patterns.

    Example usage:
        library = load_library("my_library.json")
        wrapper = LibraryWrapper(library)
        retrieved = wrapper.get_library()
    """

    def __init__(self, library: Optional[Any] = None):
        """
        Initialize the library wrapper.

        Args:
            library: Optional Library object to wrap. Can be any type
                    (typically a dict-like structure from JSON/XML parsing
                    or an actual Library class from elm-execution)
        """
        self.library = library

    def get_library(self) -> Optional[Any]:
        """
        Get the wrapped library.

        Returns:
            The wrapped Library object, or None if not set
        """
        return self.library

    def set_library(self, library: Any) -> None:
        """
        Set the wrapped library.

        Args:
            library: The Library object to wrap
        """
        self.library = library

    def __repr__(self) -> str:
        """String representation of the wrapper."""
        if self.library is None:
            return "LibraryWrapper(library=None)"
        else:
            library_type = type(self.library).__name__
            return f"LibraryWrapper(library={library_type})"
