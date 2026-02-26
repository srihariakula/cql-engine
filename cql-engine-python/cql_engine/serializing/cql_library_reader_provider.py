"""
CQL library reader provider interface for CQL engine.

Service provider interface for creating CQL library readers.
"""

from abc import ABC, abstractmethod

# Import base class - use relative import to avoid package init
try:
    from cql_engine.serializing.cql_library_reader import CqlLibraryReader
except ImportError:
    # Fallback if package structure issue
    from .cql_library_reader import CqlLibraryReader


class CqlLibraryReaderProvider(ABC):
    """
    Abstract service provider interface for creating CQL library reader instances.

    Implementations create reader instances for specific content types.

    This interface mirrors the Java CqlLibraryReaderProvider interface while using
    Python conventions and types.
    """

    @abstractmethod
    def create(self, content_type: str) -> CqlLibraryReader:
        """
        Create a CQL library reader for the specified content type.

        Args:
            content_type: The content type (e.g., "application/elm+json", "application/elm+xml")
                         If None, defaults to "application/elm+json"

        Returns:
            A CqlLibraryReader implementation for the specified content type

        Raises:
            ValueError: If the content type is not supported
        """
        pass


class DefaultCqlLibraryReaderProvider(CqlLibraryReaderProvider):
    """
    Default implementation of CqlLibraryReaderProvider.

    Provides readers for:
    - application/elm+json: JSON-based CQL libraries
    - application/elm+xml: XML-based CQL libraries
    """

    def create(self, content_type: str) -> CqlLibraryReader:
        """
        Create a CQL library reader for the specified content type.

        Args:
            content_type: The content type. Supported values:
                - "application/elm+json": Returns JsonLibraryReader
                - "application/elm+xml": Returns XmlLibraryReader
                - None: Defaults to "application/elm+json"

        Returns:
            A CqlLibraryReader implementation for the specified content type

        Raises:
            ValueError: If the content type is not supported
        """
        if content_type is None:
            content_type = "application/elm+json"

        content_type = content_type.lower().strip()

        if content_type in ("application/elm+xml", "application/xml", "text/xml"):
            from cql_engine.serializing.xml_library_reader import XmlLibraryReader
            return XmlLibraryReader()
        elif content_type in ("application/elm+json", "application/json", "text/json"):
            from cql_engine.serializing.json_library_reader import JsonLibraryReader
            return JsonLibraryReader()
        else:
            raise ValueError(
                f"Unsupported content type: {content_type}. "
                "Supported types are: application/elm+json, application/elm+xml"
            )
