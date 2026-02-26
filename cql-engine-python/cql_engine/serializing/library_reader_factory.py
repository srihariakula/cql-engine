"""
Library reader factory with service discovery.

This module provides the primary factory interface for obtaining library readers.
It uses the service provider interface pattern to discover and instantiate readers.

This replaces the Java CqlLibraryReaderFactory and provides both:
- Service discovery via entry points (for extensibility)
- Built-in default providers for JSON and XML
"""

from typing import Optional

# Import base classes - use relative imports to avoid package init issues
try:
    from cql_engine.serializing.cql_library_reader import CqlLibraryReader
    from cql_engine.serializing.cql_library_reader_provider import CqlLibraryReaderProvider
except ImportError:
    # Fallback if package structure issue
    from .cql_library_reader import CqlLibraryReader
    from .cql_library_reader_provider import CqlLibraryReaderProvider


class LibraryReaderFactory:
    """
    Factory for obtaining CQL library readers.

    This is the primary interface for getting library readers. It uses the
    service provider interface pattern to discover reader providers.

    Example usage:
        # Get reader for JSON
        reader = LibraryReaderFactory.get_reader("application/elm+json")
        library = reader.read_file("path/to/library.json")

        # Get reader for XML
        reader = LibraryReaderFactory.get_reader("application/elm+xml")
        library = reader.read_file("path/to/library.xml")

        # Get reader with auto-detection (defaults to JSON)
        reader = LibraryReaderFactory.get_reader(None)
    """

    _cached_reader_cache = {}

    def __init__(self):
        """Private constructor - this class provides only static methods."""
        raise TypeError("LibraryReaderFactory cannot be instantiated")

    @staticmethod
    def get_reader(content_type: Optional[str] = None) -> CqlLibraryReader:
        """
        Get a CQL library reader for the specified content type.

        Uses service discovery to find providers, with fallback to built-in default provider.

        Args:
            content_type: The content type to read. Supported values:
                - "application/elm+json": JSON-based libraries
                - "application/elm+xml": XML-based libraries
                - None: Defaults to JSON reader
                - Other MIME type variations are mapped to the above

        Returns:
            A CqlLibraryReader implementation for the specified content type

        Raises:
            RuntimeError: If no suitable provider is found or multiple conflicting providers exist
            ValueError: If the content type is not supported
        """
        # Use cache to avoid recreating readers for same content type
        if content_type in LibraryReaderFactory._cached_reader_cache:
            return LibraryReaderFactory._cached_reader_cache[content_type]

        # Try each provider until one succeeds
        provider = LibraryReaderFactory._get_provider()
        reader = provider.create(content_type)

        # Cache the result
        LibraryReaderFactory._cached_reader_cache[content_type] = reader

        return reader

    @staticmethod
    def _get_provider() -> CqlLibraryReaderProvider:
        """
        Get the CQL library reader provider.

        Uses service discovery via entry points if available, otherwise falls back
        to the default provider.

        Returns:
            A CqlLibraryReaderProvider implementation

        Raises:
            RuntimeError: If no provider is found or configuration is invalid
        """
        # Try to use the factory from cql_library_reader_factory for service discovery
        try:
            from cql_engine.serializing.cql_library_reader_factory import CqlLibraryReaderFactory as DiscoveryFactory
            providers = list(DiscoveryFactory.providers())

            if providers:
                # If we found providers via service discovery, validate count
                if len(providers) > 1:
                    raise RuntimeError(
                        "Multiple CqlLibraryReaderProviders found. "
                        "Only one provider should be configured."
                    )
                return providers[0]
        except (ImportError, RuntimeError):
            pass

        # Fallback to default provider
        from cql_engine.serializing.cql_library_reader_provider import DefaultCqlLibraryReaderProvider
        return DefaultCqlLibraryReaderProvider()

    @staticmethod
    def clear_cache() -> None:
        """
        Clear the reader cache.

        This is useful if you want to force recreation of readers,
        such as after changing configuration.
        """
        LibraryReaderFactory._cached_reader_cache.clear()

    @staticmethod
    def get_json_reader() -> CqlLibraryReader:
        """
        Get a JSON library reader.

        Returns:
            A CqlLibraryReader for JSON content

        Raises:
            RuntimeError: If no suitable provider is found
            ValueError: If JSON is not supported
        """
        return LibraryReaderFactory.get_reader("application/elm+json")

    @staticmethod
    def get_xml_reader() -> CqlLibraryReader:
        """
        Get an XML library reader.

        Returns:
            A CqlLibraryReader for XML content

        Raises:
            RuntimeError: If no suitable provider is found
            ValueError: If XML is not supported
        """
        return LibraryReaderFactory.get_reader("application/elm+xml")
