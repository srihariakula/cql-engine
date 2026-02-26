"""
Test suite for CQL library readers.

Tests JSON and XML readers with various input types.
"""

import unittest
import json
import tempfile
from pathlib import Path
from io import StringIO, BytesIO

from cql_engine.serializing import (
    JsonLibraryReader,
    XmlLibraryReader,
    LibraryReaderFactory,
    LibraryWrapper,
)


class TestJsonLibraryReader(unittest.TestCase):
    """Test cases for JSON library reader."""

    def setUp(self):
        """Set up test fixtures."""
        self.reader = JsonLibraryReader()
        self.sample_json = {
            "library": {
                "identifier": {"id": "TestLibrary", "version": "1.0"},
                "schemaIdentifier": {"id": "urn:hl7-org:elm", "version": "r1"},
                "usings": [],
                "statements": []
            }
        }
        self.json_string = json.dumps(self.sample_json)

    def test_read_from_string(self):
        """Test reading JSON from a string."""
        result = self.reader.read_string(self.json_string)
        self.assertEqual(result["library"]["identifier"]["id"], "TestLibrary")

    def test_read_from_file(self):
        """Test reading JSON from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_json, f)
            temp_path = f.name

        try:
            result = self.reader.read_file(temp_path)
            self.assertEqual(result["library"]["identifier"]["id"], "TestLibrary")
        finally:
            Path(temp_path).unlink()

    def test_read_from_path_object(self):
        """Test reading JSON from a Path object."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_json, f)
            temp_path = Path(f.name)

        try:
            result = self.reader.read(temp_path)
            self.assertEqual(result["library"]["identifier"]["id"], "TestLibrary")
        finally:
            temp_path.unlink()

    def test_read_from_binary_stream(self):
        """Test reading JSON from a binary stream."""
        stream = BytesIO(self.json_string.encode('utf-8'))
        result = self.reader.read_stream(stream)
        self.assertEqual(result["library"]["identifier"]["id"], "TestLibrary")

    def test_read_from_text_reader(self):
        """Test reading JSON from a text reader."""
        reader = StringIO(self.json_string)
        result = self.reader.read(reader)
        self.assertEqual(result["library"]["identifier"]["id"], "TestLibrary")

    def test_invalid_json_string(self):
        """Test reading invalid JSON raises ValueError."""
        with self.assertRaises(ValueError):
            self.reader.read_string("{invalid json")

    def test_nonexistent_file(self):
        """Test reading from nonexistent file raises IOError."""
        with self.assertRaises(IOError):
            self.reader.read_file("/nonexistent/path/library.json")


class TestXmlLibraryReader(unittest.TestCase):
    """Test cases for XML library reader."""

    def setUp(self):
        """Set up test fixtures."""
        self.reader = XmlLibraryReader()
        self.sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<library xmlns="urn:hl7-org:elm:r1">
    <identifier id="TestLibrary" version="1.0"/>
    <schemaIdentifier id="urn:hl7-org:elm" version="r1"/>
    <statements>
        <def name="Population"/>
    </statements>
</library>'''

    def test_read_from_string(self):
        """Test reading XML from a string."""
        result = self.reader.read_string(self.sample_xml)
        self.assertEqual(result["_tag"], "library")
        self.assertIn("_children", result)

    def test_read_from_file(self):
        """Test reading XML from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(self.sample_xml)
            temp_path = f.name

        try:
            result = self.reader.read_file(temp_path)
            self.assertEqual(result["_tag"], "library")
        finally:
            Path(temp_path).unlink()

    def test_read_from_binary_stream(self):
        """Test reading XML from a binary stream."""
        stream = BytesIO(self.sample_xml.encode('utf-8'))
        result = self.reader.read_stream(stream)
        self.assertEqual(result["_tag"], "library")

    def test_attributes_parsing(self):
        """Test that XML attributes are properly parsed."""
        result = self.reader.read_string(self.sample_xml)
        # The identifier element should have id and version attributes
        children = result["_children"]
        identifier = children.get("identifier")
        self.assertIsNotNone(identifier)

    def test_invalid_xml_string(self):
        """Test reading invalid XML raises ValueError."""
        invalid_xml = "<?xml version=\"1.0\"?><unclosed>"
        with self.assertRaises(ValueError):
            self.reader.read_string(invalid_xml)

    def test_nonexistent_file(self):
        """Test reading from nonexistent file raises IOError."""
        with self.assertRaises(IOError):
            self.reader.read_file("/nonexistent/path/library.xml")


class TestLibraryReaderFactory(unittest.TestCase):
    """Test cases for library reader factory."""

    def test_get_json_reader(self):
        """Test getting JSON reader from factory."""
        reader = LibraryReaderFactory.get_json_reader()
        self.assertIsNotNone(reader)
        self.assertIsInstance(reader, JsonLibraryReader)

    def test_get_xml_reader(self):
        """Test getting XML reader from factory."""
        reader = LibraryReaderFactory.get_xml_reader()
        self.assertIsNotNone(reader)
        self.assertIsInstance(reader, XmlLibraryReader)

    def test_get_reader_json(self):
        """Test getting reader for JSON content type."""
        reader = LibraryReaderFactory.get_reader("application/elm+json")
        self.assertIsInstance(reader, JsonLibraryReader)

    def test_get_reader_xml(self):
        """Test getting reader for XML content type."""
        reader = LibraryReaderFactory.get_reader("application/elm+xml")
        self.assertIsInstance(reader, XmlLibraryReader)

    def test_get_reader_default(self):
        """Test default reader (should be JSON)."""
        reader = LibraryReaderFactory.get_reader(None)
        self.assertIsInstance(reader, JsonLibraryReader)

    def test_reader_caching(self):
        """Test that readers are cached by content type."""
        reader1 = LibraryReaderFactory.get_reader("application/elm+json")
        reader2 = LibraryReaderFactory.get_reader("application/elm+json")
        self.assertIs(reader1, reader2)

    def test_clear_cache(self):
        """Test clearing reader cache."""
        reader1 = LibraryReaderFactory.get_reader("application/elm+json")
        LibraryReaderFactory.clear_cache()
        reader2 = LibraryReaderFactory.get_reader("application/elm+json")
        self.assertIsNot(reader1, reader2)


class TestLibraryWrapper(unittest.TestCase):
    """Test cases for library wrapper."""

    def test_wrap_library(self):
        """Test wrapping a library object."""
        library = {"name": "TestLibrary"}
        wrapper = LibraryWrapper(library)
        self.assertEqual(wrapper.get_library(), library)

    def test_set_library(self):
        """Test setting a library in wrapper."""
        wrapper = LibraryWrapper()
        library = {"name": "TestLibrary"}
        wrapper.set_library(library)
        self.assertEqual(wrapper.get_library(), library)

    def test_none_library(self):
        """Test wrapper with None library."""
        wrapper = LibraryWrapper(None)
        self.assertIsNone(wrapper.get_library())

    def test_wrapper_repr(self):
        """Test string representation of wrapper."""
        library = {"name": "Test"}
        wrapper = LibraryWrapper(library)
        repr_str = repr(wrapper)
        self.assertIn("LibraryWrapper", repr_str)


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""

    def test_json_workflow(self):
        """Test complete JSON reading workflow."""
        sample_library = {
            "library": {
                "identifier": {"id": "MyLibrary", "version": "1.0"},
                "statements": []
            }
        }

        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_library, f)
            temp_path = f.name

        try:
            # Read using factory
            reader = LibraryReaderFactory.get_json_reader()
            library = reader.read_file(temp_path)

            # Wrap library
            wrapper = LibraryWrapper(library)

            # Verify
            self.assertEqual(
                wrapper.get_library()["library"]["identifier"]["id"],
                "MyLibrary"
            )
        finally:
            Path(temp_path).unlink()

    def test_xml_workflow(self):
        """Test complete XML reading workflow."""
        sample_xml = '''<?xml version="1.0"?>
<library>
    <identifier id="MyLibrary" version="1.0"/>
</library>'''

        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_xml)
            temp_path = f.name

        try:
            # Read using factory
            reader = LibraryReaderFactory.get_xml_reader()
            library = reader.read_file(temp_path)

            # Wrap library
            wrapper = LibraryWrapper(library)

            # Verify
            self.assertEqual(wrapper.get_library()["_tag"], "library")
        finally:
            Path(temp_path).unlink()


if __name__ == '__main__':
    unittest.main()
