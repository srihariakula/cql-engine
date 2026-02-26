"""
JSON-based CQL library reader using Python's standard json module.

Provides deserialization of CQL libraries from JSON format,
replacing Jackson JSON reader functionality.
"""

import json
from io import StringIO, TextIOBase
from pathlib import Path
from typing import Union, BinaryIO, TextIO, Any, Dict
from urllib.parse import urlparse
import urllib.request

# Import base class - use relative import to avoid package init
try:
    from cql_engine.serializing.cql_library_reader import CqlLibraryReader
except ImportError:
    # Fallback if package structure issue
    from .cql_library_reader import CqlLibraryReader


class JsonLibraryReader(CqlLibraryReader):
    """
    Reads CQL libraries from JSON sources.

    Supports reading from:
    - File paths (Path or str)
    - URLs and URIs
    - JSON strings
    - Input streams (binary or text)
    - Reader objects
    """

    def __init__(self):
        """Initialize the JSON library reader."""
        pass

    def read(self, source: Union[Path, str, BinaryIO, TextIO]) -> Any:
        """
        Read a CQL library from a JSON source.

        Args:
            source: The source to read from (file, URL, URI, stream, string, or reader)

        Returns:
            The parsed Library object (deserialized JSON)

        Raises:
            IOError: If there's an error reading from the source
            ValueError: If the content cannot be parsed as JSON
        """
        # Handle different source types
        if isinstance(source, str):
            # Could be a URI, file path, or JSON string
            return self._read_from_string(source)
        elif isinstance(source, Path):
            # File path
            return self._read_from_file(source)
        elif isinstance(source, TextIOBase) or hasattr(source, 'read'):
            # Text reader or similar
            return self._read_from_reader(source)
        else:
            # Try to treat as binary stream
            return self._read_from_stream(source)

    def _read_from_string(self, content: str) -> Any:
        """
        Read from a string that could be a URI, file path, or JSON string.

        Args:
            content: String content (URI, file path, or JSON)

        Returns:
            The parsed Library object

        Raises:
            IOError: If file/URL cannot be accessed
            ValueError: If content cannot be parsed as JSON
        """
        # Try to parse as URI first
        parsed = urlparse(content)
        if parsed.scheme in ('http', 'https', 'ftp'):
            return self._read_from_url(content)

        # Try as file path
        try:
            return self._read_from_file(Path(content))
        except (FileNotFoundError, OSError):
            # Not a file, try as JSON string
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Could not parse content as JSON or locate as file: {str(e)}")

    def _read_from_file(self, file_path: Union[str, Path]) -> Any:
        """
        Read a JSON library from a file.

        Args:
            file_path: Path to the JSON file

        Returns:
            The parsed Library object

        Raises:
            IOError: If the file cannot be read
            ValueError: If the file content is not valid JSON
        """
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {file_path}: {str(e)}")
        except (FileNotFoundError, IOError) as e:
            raise IOError(f"Cannot read file {file_path}: {str(e)}")

    def _read_from_url(self, url: str) -> Any:
        """
        Read a JSON library from a URL.

        Args:
            url: The URL to fetch from

        Returns:
            The parsed Library object

        Raises:
            IOError: If the URL cannot be accessed
            ValueError: If the response content is not valid JSON
        """
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
                return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from URL {url}: {str(e)}")
        except Exception as e:
            raise IOError(f"Cannot fetch URL {url}: {str(e)}")

    def _read_from_stream(self, stream: BinaryIO) -> Any:
        """
        Read a JSON library from a binary stream.

        Args:
            stream: Binary input stream

        Returns:
            The parsed Library object

        Raises:
            IOError: If there's an error reading from the stream
            ValueError: If the stream content is not valid JSON
        """
        try:
            content = stream.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from stream: {str(e)}")
        except Exception as e:
            raise IOError(f"Cannot read from stream: {str(e)}")

    def _read_from_reader(self, reader: TextIO) -> Any:
        """
        Read a JSON library from a text reader.

        Args:
            reader: Text reader

        Returns:
            The parsed Library object

        Raises:
            IOError: If there's an error reading from the reader
            ValueError: If the reader content is not valid JSON
        """
        try:
            content = reader.read()
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from reader: {str(e)}")
        except Exception as e:
            raise IOError(f"Cannot read from reader: {str(e)}")

    # Convenience methods matching Java API

    def read_file(self, file_path: Union[str, Path]) -> Any:
        """
        Read a CQL library from a file.

        Args:
            file_path: Path to the JSON file

        Returns:
            The parsed Library object
        """
        return self._read_from_file(file_path)

    def read_url(self, url: str) -> Any:
        """
        Read a CQL library from a URL.

        Args:
            url: The URL to fetch from

        Returns:
            The parsed Library object
        """
        return self._read_from_url(url)

    def read_uri(self, uri: str) -> Any:
        """
        Read a CQL library from a URI.

        Args:
            uri: The URI to read from

        Returns:
            The parsed Library object
        """
        return self._read_from_string(uri)

    def read_string(self, content: str) -> Any:
        """
        Read a CQL library from a JSON string.

        Args:
            content: JSON string content

        Returns:
            The parsed Library object
        """
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {str(e)}")

    def read_stream(self, stream: BinaryIO) -> Any:
        """
        Read a CQL library from a binary stream.

        Args:
            stream: Binary input stream

        Returns:
            The parsed Library object
        """
        return self._read_from_stream(stream)

    def read_text_reader(self, reader: TextIO) -> Any:
        """
        Read a CQL library from a text reader.

        Args:
            reader: Text reader

        Returns:
            The parsed Library object
        """
        return self._read_from_reader(reader)
