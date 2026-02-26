"""
CQL library reader factory for CQL engine.

Provides factory methods for creating CQL library readers using service provider interface.
"""

from typing import Iterator, Optional
import importlib

# Import base classes - use relative imports to avoid package init issues
try:
    from cql_engine.serializing.cql_library_reader_provider import CqlLibraryReaderProvider
    from cql_engine.serializing.cql_library_reader import CqlLibraryReader
except ImportError:
    # Fallback if package structure issue
    from .cql_library_reader_provider import CqlLibraryReaderProvider
    from .cql_library_reader import CqlLibraryReader


class CqlLibraryReaderFactory:
    """
    Factory for obtaining CQL library readers.

    Uses the service provider interface pattern to discover and instantiate
    CqlLibraryReaderProvider implementations.
    """

    def __init__(self):
        """Private constructor - this class provides only static methods."""
        pass

    @staticmethod
    def providers(refresh: bool = False) -> Iterator[CqlLibraryReaderProvider]:
        """
        Get an iterator of CQL library reader providers.

        Uses Python's importlib to discover service providers, with fallback
        to built-in providers if none are found via entry points.

        Args:
            refresh: If True, reload providers from the path

        Returns:
            Iterator of CqlLibraryReaderProvider implementations
        """
        # In Python, we'd typically use entry points or importlib.metadata
        # This is a simplified version that can be extended with proper
        # service discovery
        providers_list = []

        # Try to discover providers from entry points
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            if hasattr(eps, 'select'):
                # Python 3.10+
                group = eps.select(group='cql_engine.reader_provider')
            else:
                # Python 3.9
                group = eps.get('cql_engine.reader_provider', [])

            for ep in group:
                try:
                    provider_class = ep.load()
                    providers_list.append(provider_class())
                except Exception:
                    pass
        except (ImportError, AttributeError):
            pass

        # If no providers found via entry points, use built-in provider
        if not providers_list:
            try:
                from cql_engine.serializing.cql_library_reader_provider import DefaultCqlLibraryReaderProvider
                providers_list.append(DefaultCqlLibraryReaderProvider())
            except ImportError:
                pass

        return iter(providers_list)

    @staticmethod
    def get_reader(content_type: str) -> CqlLibraryReader:
        """
        Get a CQL library reader for the specified content type.

        Args:
            content_type: The content type to read (e.g., "application/json")

        Returns:
            A CqlLibraryReader for the specified content type

        Raises:
            RuntimeError: If no provider is found or multiple providers are found
        """
        providers = CqlLibraryReaderFactory.providers(refresh=False)
        provider_list = list(providers)

        if not provider_list:
            raise RuntimeError(
                "No CqlLibraryReaderProviders found on the classpath. "
                "You need to add a reference to one of the 'engine.jackson' or 'engine.jaxb' packages, "
                "or provide your own implementation."
            )

        if len(provider_list) > 1:
            raise RuntimeError(
                "Multiple CqlLibraryReaderProviders found on the classpath. "
                "You need to remove a reference to either the 'engine.jackson' or the 'engine.jaxb' package"
            )

        provider = provider_list[0]
        return provider.create(content_type)
