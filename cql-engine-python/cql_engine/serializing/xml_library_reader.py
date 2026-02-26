"""
XML-based CQL library reader using Python's xml.etree.ElementTree.

Provides deserialization of CQL libraries from XML format,
replacing Jackson XML reader and JAXB XML reader functionality.
"""

import xml.etree.ElementTree as ET
from io import StringIO, BytesIO, TextIOBase
from pathlib import Path
from typing import Union, BinaryIO, TextIO, Any, Dict, Optional
from urllib.parse import urlparse
import urllib.request
from xml.dom import minidom

# Import base class - use relative import to avoid package init
try:
    from cql_engine.serializing.cql_library_reader import CqlLibraryReader
except ImportError:
    # Fallback if package structure issue
    from .cql_library_reader import CqlLibraryReader


class XmlLibraryReader(CqlLibraryReader):
    """
    Reads CQL libraries from XML sources.

    Supports reading from:
    - File paths (Path or str)
    - URLs and URIs
    - XML strings
    - Input streams (binary or text)
    - Reader objects

    Handles XML parsing and namespace resolution for CQL ELM format.
    """

    # Common namespaces used in CQL ELM XML
    NAMESPACES = {
        'elm': 'urn:hl7-org:elm:r1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xs': 'http://www.w3.org/2001/XMLSchema',
    }

    def __init__(self):
        """Initialize the XML library reader."""
        pass

    def read(self, source: Union[Path, str, BinaryIO, TextIO]) -> Any:
        """
        Read a CQL library from an XML source.

        Args:
            source: The source to read from (file, URL, URI, stream, string, or reader)

        Returns:
            The parsed Library object (deserialized XML as dict-like structure)

        Raises:
            IOError: If there's an error reading from the source
            ValueError: If the content cannot be parsed as XML
        """
        # Handle different source types
        if isinstance(source, str):
            # Could be a URI, file path, or XML string
            return self._read_from_string(source)
        elif isinstance(source, Path):
            # File path
            return self._read_from_file(source)
        elif isinstance(source, TextIOBase) or (hasattr(source, 'read') and hasattr(source, 'mode') and 'b' not in source.mode):
            # Text reader or similar
            return self._read_from_reader(source)
        else:
            # Try to treat as binary stream
            return self._read_from_stream(source)

    def _read_from_string(self, content: str) -> Any:
        """
        Read from a string that could be a URI, file path, or XML string.

        Args:
            content: String content (URI, file path, or XML)

        Returns:
            The parsed Library object

        Raises:
            IOError: If file/URL cannot be accessed
            ValueError: If content cannot be parsed as XML
        """
        # Try to parse as URI first
        parsed = urlparse(content)
        if parsed.scheme in ('http', 'https', 'ftp'):
            return self._read_from_url(content)

        # Try as file path
        try:
            return self._read_from_file(Path(content))
        except (FileNotFoundError, OSError):
            # Not a file, try as XML string
            try:
                return self._parse_xml_string(content)
            except ET.ParseError as e:
                raise ValueError(f"Could not parse content as XML or locate as file: {str(e)}")

    def _read_from_file(self, file_path: Union[str, Path]) -> Any:
        """
        Read an XML library from a file.

        Args:
            file_path: Path to the XML file

        Returns:
            The parsed Library object

        Raises:
            IOError: If the file cannot be read
            ValueError: If the file content is not valid XML
        """
        file_path = Path(file_path)
        try:
            with open(file_path, 'rb') as f:
                return self._parse_xml_stream(f)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML in file {file_path}: {str(e)}")
        except (FileNotFoundError, IOError) as e:
            raise IOError(f"Cannot read file {file_path}: {str(e)}")

    def _read_from_url(self, url: str) -> Any:
        """
        Read an XML library from a URL.

        Args:
            url: The URL to fetch from

        Returns:
            The parsed Library object

        Raises:
            IOError: If the URL cannot be accessed
            ValueError: If the response content is not valid XML
        """
        try:
            with urllib.request.urlopen(url) as response:
                return self._parse_xml_stream(response)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML from URL {url}: {str(e)}")
        except Exception as e:
            raise IOError(f"Cannot fetch URL {url}: {str(e)}")

    def _read_from_stream(self, stream: BinaryIO) -> Any:
        """
        Read an XML library from a binary stream.

        Args:
            stream: Binary input stream

        Returns:
            The parsed Library object

        Raises:
            IOError: If there's an error reading from the stream
            ValueError: If the stream content is not valid XML
        """
        try:
            return self._parse_xml_stream(stream)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML from stream: {str(e)}")
        except Exception as e:
            raise IOError(f"Cannot read from stream: {str(e)}")

    def _read_from_reader(self, reader: TextIO) -> Any:
        """
        Read an XML library from a text reader.

        Args:
            reader: Text reader

        Returns:
            The parsed Library object

        Raises:
            IOError: If there's an error reading from the reader
            ValueError: If the reader content is not valid XML
        """
        try:
            content = reader.read()
            return self._parse_xml_string(content)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML from reader: {str(e)}")
        except Exception as e:
            raise IOError(f"Cannot read from reader: {str(e)}")

    def _parse_xml_string(self, xml_string: str) -> Dict[str, Any]:
        """
        Parse XML string into a dict-like structure.

        Args:
            xml_string: XML content as string

        Returns:
            Dictionary representation of the XML tree

        Raises:
            ET.ParseError: If XML is malformed
        """
        root = ET.fromstring(xml_string)
        return self._element_to_dict(root)

    def _parse_xml_stream(self, stream: Union[BinaryIO, Any]) -> Dict[str, Any]:
        """
        Parse XML from a stream into a dict-like structure.

        Args:
            stream: Binary stream or file-like object with read() method

        Returns:
            Dictionary representation of the XML tree

        Raises:
            ET.ParseError: If XML is malformed
        """
        tree = ET.parse(stream)
        root = tree.getroot()
        return self._element_to_dict(root)

    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        Convert an XML Element to a dictionary.

        Recursively processes child elements and attributes.

        Args:
            element: The ElementTree Element to convert

        Returns:
            Dictionary representation of the element
        """
        result = {}

        # Add element tag (remove namespace)
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]
        result['_tag'] = tag

        # Add attributes
        if element.attrib:
            attrs = {}
            for key, value in element.attrib.items():
                # Clean up namespace in attribute names
                attr_name = key
                if '}' in attr_name:
                    attr_name = attr_name.split('}', 1)[1]
                attrs[attr_name] = value
            result['_attributes'] = attrs

        # Add text content
        if element.text and element.text.strip():
            result['_text'] = element.text.strip()

        # Add child elements
        children = {}
        for child in element:
            child_tag = child.tag
            if '}' in child_tag:
                child_tag = child_tag.split('}', 1)[1]

            child_dict = self._element_to_dict(child)

            if child_tag in children:
                # Multiple children with same tag - convert to list
                if not isinstance(children[child_tag], list):
                    children[child_tag] = [children[child_tag]]
                children[child_tag].append(child_dict)
            else:
                children[child_tag] = child_dict

        if children:
            result['_children'] = children

        return result

    # Convenience methods matching Java API

    def read_file(self, file_path: Union[str, Path]) -> Any:
        """
        Read a CQL library from an XML file.

        Args:
            file_path: Path to the XML file

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
        Read a CQL library from an XML string.

        Args:
            content: XML string content

        Returns:
            The parsed Library object
        """
        return self._parse_xml_string(content)

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


class XmlLibraryReaderLxml(XmlLibraryReader):
    """
    Extended XML library reader using lxml for enhanced XML support.

    Requires: pip install lxml

    Provides additional features over the standard ElementTree version:
    - Better namespace handling
    - XPath support
    - Better performance on large files
    - Better error messages
    """

    def __init__(self):
        """Initialize the lxml-based XML library reader."""
        try:
            from lxml import etree
            self.etree = etree
        except ImportError:
            raise ImportError(
                "lxml is required for XmlLibraryReaderLxml. "
                "Install it with: pip install lxml"
            )

    def _parse_xml_string(self, xml_string: str) -> Dict[str, Any]:
        """
        Parse XML string using lxml.

        Args:
            xml_string: XML content as string

        Returns:
            Dictionary representation of the XML tree

        Raises:
            Exception: If XML is malformed
        """
        try:
            root = self.etree.fromstring(xml_string.encode('utf-8'))
            return self._element_to_dict(root)
        except self.etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML: {str(e)}")

    def _parse_xml_stream(self, stream: Union[BinaryIO, Any]) -> Dict[str, Any]:
        """
        Parse XML from a stream using lxml.

        Args:
            stream: Binary stream or file-like object

        Returns:
            Dictionary representation of the XML tree

        Raises:
            Exception: If XML is malformed
        """
        try:
            tree = self.etree.parse(stream)
            root = tree.getroot()
            return self._element_to_dict(root)
        except self.etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML: {str(e)}")

    def _element_to_dict(self, element: Any) -> Dict[str, Any]:
        """
        Convert an lxml Element to a dictionary.

        Args:
            element: The lxml Element to convert

        Returns:
            Dictionary representation of the element
        """
        result = {}

        # Get tag name without namespace
        tag = element.tag
        if isinstance(tag, str):
            if '}' in tag:
                tag = tag.split('}', 1)[1]
            result['_tag'] = tag

        # Add attributes
        if element.attrib:
            attrs = {}
            for key, value in element.attrib.items():
                attr_name = key
                if '}' in attr_name:
                    attr_name = attr_name.split('}', 1)[1]
                attrs[attr_name] = value
            result['_attributes'] = attrs

        # Add text content
        if element.text and element.text.strip():
            result['_text'] = element.text.strip()

        # Add child elements
        children = {}
        for child in element:
            child_tag = child.tag
            if isinstance(child_tag, str):
                if '}' in child_tag:
                    child_tag = child_tag.split('}', 1)[1]

                child_dict = self._element_to_dict(child)

                if child_tag in children:
                    if not isinstance(children[child_tag], list):
                        children[child_tag] = [children[child_tag]]
                    children[child_tag].append(child_dict)
                else:
                    children[child_tag] = child_dict

        if children:
            result['_children'] = children

        return result
