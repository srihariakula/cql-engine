#!/usr/bin/env python3
"""
Standalone test script for serializing module (without importing main cql_engine package).
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from io import BytesIO

# Add the cql_engine/serializing directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cql_engine/serializing'))

# Import directly from module files
import json_library_reader
import xml_library_reader
import library_reader_factory
import library_wrapper
import cql_library_reader
import cql_library_reader_provider

JsonLibraryReader = json_library_reader.JsonLibraryReader
XmlLibraryReader = xml_library_reader.XmlLibraryReader
LibraryReaderFactory = library_reader_factory.LibraryReaderFactory
LibraryWrapper = library_wrapper.LibraryWrapper

print("=" * 60)
print("CQL Engine Serializing Module - Standalone Tests")
print("=" * 60)

# Test JSON reader
print("\nTesting JSON Library Reader...")
reader = JsonLibraryReader()

# Test from string
json_str = '{"library": {"name": "TestLib"}}'
result = reader.read_string(json_str)
assert result["library"]["name"] == "TestLib"
print("  ✓ String parsing works")

# Test from file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump({"test": "data"}, f)
    temp_path = f.name

result = reader.read_file(temp_path)
assert result["test"] == "data"
print("  ✓ File reading works")
Path(temp_path).unlink()

# Test from stream
stream = BytesIO(b'{"stream": "test"}')
result = reader.read(stream)
assert result["stream"] == "test"
print("  ✓ Stream reading works")

# Test from URL simulation (can't do actual URLs, but test URI parsing)
# Test file path recognition
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump({"uri_test": "works"}, f)
    temp_path = f.name

result = reader.read(temp_path)
assert result["uri_test"] == "works"
print("  ✓ Path URI recognition works")
Path(temp_path).unlink()

# Test error handling
try:
    reader.read_string("{invalid json")
    print("  ✗ ERROR: Should have raised ValueError for invalid JSON")
    sys.exit(1)
except ValueError:
    print("  ✓ Error handling for invalid JSON works")

try:
    reader.read_file("/nonexistent/file.json")
    print("  ✗ ERROR: Should have raised IOError for nonexistent file")
    sys.exit(1)
except IOError:
    print("  ✓ Error handling for nonexistent file works")

# Test XML reader
print("\nTesting XML Library Reader...")
reader = XmlLibraryReader()

# Test from string
xml_str = '<?xml version="1.0"?><library><name>Test</name></library>'
result = reader.read_string(xml_str)
assert result["_tag"] == "library"
print("  ✓ String parsing works")

# Test from file
with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
    f.write(xml_str)
    temp_path = f.name

result = reader.read_file(temp_path)
assert result["_tag"] == "library"
print("  ✓ File reading works")
Path(temp_path).unlink()

# Test attributes and children parsing
xml_with_attrs = '''<?xml version="1.0"?>
<library version="1.0">
    <identifier id="test"/>
    <statement><name>Stmt1</name></statement>
</library>'''
result = reader.read_string(xml_with_attrs)
assert "_attributes" in result
assert result["_attributes"]["version"] == "1.0"
assert "identifier" in result["_children"]
print("  ✓ Attributes and children parsing works")

# Test namespace handling
xml_with_ns = '''<?xml version="1.0"?>
<library xmlns="urn:hl7-org:elm:r1">
    <identifier id="test"/>
</library>'''
result = reader.read_string(xml_with_ns)
assert result["_tag"] == "library"
print("  ✓ Namespace handling works")

# Test error handling
try:
    reader.read_string("<?xml version=\"1.0\"?><unclosed>")
    print("  ✗ ERROR: Should have raised ValueError for invalid XML")
    sys.exit(1)
except ValueError:
    print("  ✓ Error handling for invalid XML works")

try:
    reader.read_file("/nonexistent/file.xml")
    print("  ✗ ERROR: Should have raised IOError for nonexistent file")
    sys.exit(1)
except IOError:
    print("  ✓ Error handling for nonexistent file works")

# Test Factory
print("\nTesting Library Reader Factory...")
json_reader = LibraryReaderFactory.get_json_reader()
assert isinstance(json_reader, JsonLibraryReader)
print("  ✓ get_json_reader works")

xml_reader = LibraryReaderFactory.get_xml_reader()
assert isinstance(xml_reader, XmlLibraryReader)
print("  ✓ get_xml_reader works")

reader = LibraryReaderFactory.get_reader("application/elm+json")
assert isinstance(reader, JsonLibraryReader)
print("  ✓ get_reader with JSON content type works")

reader = LibraryReaderFactory.get_reader("application/elm+xml")
assert isinstance(reader, XmlLibraryReader)
print("  ✓ get_reader with XML content type works")

# Test caching
reader1 = LibraryReaderFactory.get_reader("application/elm+json")
reader2 = LibraryReaderFactory.get_reader("application/elm+json")
assert reader1 is reader2
print("  ✓ Reader caching works")

# Test cache clearing
LibraryReaderFactory.clear_cache()
reader3 = LibraryReaderFactory.get_reader("application/elm+json")
assert reader1 is not reader3
print("  ✓ Cache clearing works")

# Test Library Wrapper
print("\nTesting Library Wrapper...")
library = {"name": "Test", "version": "1.0"}
wrapper = LibraryWrapper(library)
assert wrapper.get_library() == library
print("  ✓ Constructor and get_library work")

wrapper2 = LibraryWrapper()
assert wrapper2.get_library() is None
wrapper2.set_library({"new": "lib"})
assert wrapper2.get_library()["new"] == "lib"
print("  ✓ Initialization with None and set_library work")

repr_str = repr(wrapper)
assert "LibraryWrapper" in repr_str
assert "dict" in repr_str
print("  ✓ String representation works")

# Test End-to-End Workflows
print("\nTesting End-to-End Workflows...")

# JSON workflow
sample_library = {
    "library": {
        "identifier": {"id": "MyLibrary", "version": "1.0"},
        "statements": []
    }
}

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(sample_library, f)
    temp_path = f.name

try:
    reader = LibraryReaderFactory.get_json_reader()
    library = reader.read_file(temp_path)
    wrapper = LibraryWrapper(library)
    assert wrapper.get_library()["library"]["identifier"]["id"] == "MyLibrary"
    print("  ✓ JSON workflow works")
finally:
    Path(temp_path).unlink()

# XML workflow
sample_xml = '''<?xml version="1.0"?>
<library>
    <identifier id="MyLibrary" version="1.0"/>
    <statements/>
</library>'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
    f.write(sample_xml)
    temp_path = f.name

try:
    reader = LibraryReaderFactory.get_xml_reader()
    library = reader.read_file(temp_path)
    wrapper = LibraryWrapper(library)
    assert wrapper.get_library()["_tag"] == "library"
    print("  ✓ XML workflow works")
finally:
    Path(temp_path).unlink()

# Test provider
print("\nTesting Service Provider Interface...")
provider = cql_library_reader_provider.DefaultCqlLibraryReaderProvider()
reader = provider.create("application/elm+json")
assert isinstance(reader, JsonLibraryReader)
print("  ✓ DefaultCqlLibraryReaderProvider creates JSON reader")

reader = provider.create("application/elm+xml")
assert isinstance(reader, XmlLibraryReader)
print("  ✓ DefaultCqlLibraryReaderProvider creates XML reader")

print("\n" + "=" * 60)
print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
print("=" * 60)
