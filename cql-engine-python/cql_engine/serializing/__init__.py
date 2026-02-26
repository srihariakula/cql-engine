"""
CQL Engine serializing module.

Provides abstractions for reading and deserializing CQL libraries in JSON and XML formats.

This unified module replaces the separate Jackson and JAXB modules from the Java implementation,
providing both JSON and XML support through Python's standard library and optional lxml.

Main Components:
- CqlLibraryReader: Abstract base class for library readers
- JsonLibraryReader: Reads JSON-format CQL libraries
- XmlLibraryReader: Reads XML-format CQL libraries
- LibraryReaderFactory: Factory for obtaining appropriate readers
- CqlLibraryReaderProvider: Service provider interface for reader creation
- LibraryWrapper: Simple wrapper for library objects

Usage Examples:
    # Using the factory (recommended)
    from cql_engine.serializing import LibraryReaderFactory

    reader = LibraryReaderFactory.get_reader("application/elm+json")
    library = reader.read_file("path/to/library.json")

    # Direct usage of specific readers
    from cql_engine.serializing import JsonLibraryReader, XmlLibraryReader

    json_reader = JsonLibraryReader()
    library = json_reader.read_file("library.json")

    xml_reader = XmlLibraryReader()
    library = xml_reader.read_file("library.xml")
"""

from cql_engine.serializing.cql_library_reader import CqlLibraryReader, Library
from cql_engine.serializing.cql_library_reader_provider import (
    CqlLibraryReaderProvider,
    DefaultCqlLibraryReaderProvider,
)
from cql_engine.serializing.cql_library_reader_factory import CqlLibraryReaderFactory
from cql_engine.serializing.library_reader_factory import LibraryReaderFactory
from cql_engine.serializing.json_library_reader import JsonLibraryReader
from cql_engine.serializing.xml_library_reader import XmlLibraryReader, XmlLibraryReaderLxml
from cql_engine.serializing.library_wrapper import LibraryWrapper

__all__ = [
    # Core interfaces
    'CqlLibraryReader',
    'Library',
    'CqlLibraryReaderProvider',
    'DefaultCqlLibraryReaderProvider',

    # Factories
    'CqlLibraryReaderFactory',
    'LibraryReaderFactory',

    # Concrete readers
    'JsonLibraryReader',
    'XmlLibraryReader',
    'XmlLibraryReaderLxml',

    # Wrapper
    'LibraryWrapper',
]
