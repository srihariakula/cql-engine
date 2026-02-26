"""
CQL library reader interface for CQL engine.

Provides abstraction for reading CQL libraries from various sources.
"""

from abc import ABC, abstractmethod
from typing import Union, BinaryIO, TextIO, Any
from pathlib import Path
from urllib.parse import urlparse


class Library:
    """
    Represents a parsed CQL Library.

    This is a placeholder for the actual ELM Library type from cql-elm-execution.
    In practice, this will be replaced with the actual Library class from
    the elm execution module.
    """
    pass


class CqlLibraryReader(ABC):
    """
    Abstract base class for reading CQL libraries from various sources.

    Implementations can read from:
    - Files and file paths
    - URLs and URIs
    - Strings (JSON/XML content)
    - Binary streams (InputStream)
    - Text readers

    This interface mirrors the Java CqlLibraryReader interface while using
    Python conventions and types.
    """

    @abstractmethod
    def read(self, source: Union[Path, str, BinaryIO, TextIO]) -> Any:
        """
        Read a CQL library from a source.

        This is the primary method that subclasses must implement.
        It should handle different source types and deserialize the content
        into a Library object.

        Args:
            source: The source to read from. Can be:
                - Path or str (file path, URL, or URI)
                - BinaryIO (binary stream)
                - TextIO (text reader)

        Returns:
            The parsed Library object

        Raises:
            IOError: If there's an error reading from the source
            ValueError: If the content cannot be parsed as a library
        """
        pass

    def read_file(self, file_path: Union[str, Path]) -> Any:
        """
        Read a CQL library from a file.

        Args:
            file_path: Path to the file (as string or Path object)

        Returns:
            The parsed Library

        Raises:
            IOError: If there's an error reading the file
            ValueError: If the file content is invalid
        """
        return self.read(file_path)

    def read_url(self, url: str) -> Any:
        """
        Read a CQL library from a URL.

        Args:
            url: The URL to read from (HTTP, HTTPS, or FTP)

        Returns:
            The parsed Library

        Raises:
            IOError: If there's an error fetching the URL
            ValueError: If the URL content is invalid
        """
        return self.read(url)

    def read_uri(self, uri: str) -> Any:
        """
        Read a CQL library from a URI.

        The URI can be:
        - A URL (http://, https://, ftp://)
        - A file path

        Args:
            uri: The URI to read from

        Returns:
            The parsed Library

        Raises:
            IOError: If there's an error reading the URI
            ValueError: If the content is invalid
        """
        return self.read(uri)

    def read_string(self, content: str) -> Any:
        """
        Read a CQL library from a string.

        Args:
            content: The string content (JSON or XML)

        Returns:
            The parsed Library

        Raises:
            ValueError: If the string content is invalid
        """
        return self.read(content)

    def read_stream(self, stream: BinaryIO) -> Any:
        """
        Read a CQL library from a binary stream.

        Args:
            stream: The binary stream to read from

        Returns:
            The parsed Library

        Raises:
            IOError: If there's an error reading the stream
            ValueError: If the stream content is invalid
        """
        return self.read(stream)

    def read_text_reader(self, reader: TextIO) -> Any:
        """
        Read a CQL library from a text reader.

        Args:
            reader: The text reader to read from

        Returns:
            The parsed Library

        Raises:
            IOError: If there's an error reading the reader
            ValueError: If the reader content is invalid
        """
        return self.read(reader)
