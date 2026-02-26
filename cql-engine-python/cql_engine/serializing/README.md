# CQL Engine Serializing Module

This module provides unified serialization support for reading CQL (Clinical Quality Language) libraries in JSON and XML formats. It replaces the separate Jackson and JAXB modules from the Java CQL engine, consolidating functionality into a single Pythonic interface.

## Overview

The serializing module provides:
- **JsonLibraryReader**: Reads CQL libraries in JSON format using Python's built-in `json` module
- **XmlLibraryReader**: Reads CQL libraries in XML format using Python's `xml.etree.ElementTree`
- **XmlLibraryReaderLxml**: Optional enhanced XML reader using `lxml` for better XML support
- **LibraryReaderFactory**: Factory for obtaining appropriate readers with service discovery
- **CqlLibraryReaderProvider**: Service provider interface for extensibility

## Installation

The JSON reader requires only Python's standard library.

For enhanced XML support using lxml:
```bash
pip install lxml
```

## Quick Start

### Using the Factory (Recommended)

```python
from cql_engine.serializing import LibraryReaderFactory

# Get a reader for JSON
json_reader = LibraryReaderFactory.get_reader("application/elm+json")
library = json_reader.read_file("path/to/library.json")

# Get a reader for XML
xml_reader = LibraryReaderFactory.get_reader("application/elm+xml")
library = xml_reader.read_file("path/to/library.xml")

# Default to JSON if content type is not specified
reader = LibraryReaderFactory.get_reader(None)
library = reader.read_string(json_content)
```

### Direct Reader Usage

```python
from cql_engine.serializing import JsonLibraryReader, XmlLibraryReader

# JSON reading
json_reader = JsonLibraryReader()
library = json_reader.read_file("library.json")

# XML reading
xml_reader = XmlLibraryReader()
library = xml_reader.read_file("library.xml")

# Read from URL
library = json_reader.read_url("https://example.com/library.json")

# Read from string
json_string = '{"library": {...}}'
library = json_reader.read_string(json_string)

# Read from stream
with open("library.json", "rb") as f:
    library = json_reader.read(f)
```

## Module Components

### CqlLibraryReader (Abstract Base Class)

The abstract interface that all readers implement.

**Methods:**
- `read(source)` - Primary read method (abstract, must be implemented)
- `read_file(file_path)` - Read from a file path
- `read_url(url)` - Read from a URL
- `read_uri(uri)` - Read from a URI (file path or URL)
- `read_string(content)` - Read from a string
- `read_stream(stream)` - Read from a binary stream
- `read_text_reader(reader)` - Read from a text reader

### JsonLibraryReader

Reads CQL libraries in JSON format.

**Features:**
- Uses Python's standard `json` module
- Automatically detects JSON strings vs file paths vs URIs
- Supports binary and text streams
- Proper error handling with detailed messages

**Example:**
```python
from cql_engine.serializing import JsonLibraryReader

reader = JsonLibraryReader()

# From file
library = reader.read_file("library.json")

# From string
library = reader.read_string('{"library": {"name": "MyLibrary"}}')

# From URL
library = reader.read_url("https://example.com/library.json")

# From stream
import io
stream = io.BytesIO(b'{"library": {...}}')
library = reader.read_stream(stream)
```

### XmlLibraryReader

Reads CQL libraries in XML format using ElementTree.

**Features:**
- Uses Python's built-in `xml.etree.ElementTree`
- Converts XML elements to dictionary representation
- Handles namespaces properly
- Supports multiple child elements with the same tag (converts to list)

**XML Structure Conversion:**
The reader converts XML elements to dictionaries with the following keys:
- `_tag`: Element tag name (without namespace)
- `_attributes`: Dictionary of element attributes
- `_text`: Text content of the element
- `_children`: Dictionary of child elements

**Example:**
```python
from cql_engine.serializing import XmlLibraryReader

reader = XmlLibraryReader()

# From file
library = reader.read_file("library.xml")

# From string
xml_string = '''<?xml version="1.0"?>
<library>
  <metadata>
    <identifier value="MyLibrary"/>
  </metadata>
</library>'''
library = reader.read_string(xml_string)
```

### XmlLibraryReaderLxml

Enhanced XML reader using the `lxml` library (optional dependency).

**Advantages over ElementTree:**
- Better error messages for malformed XML
- XPath support (can be added)
- Better performance on large files
- More robust namespace handling

**Installation:**
```bash
pip install lxml
```

**Example:**
```python
from cql_engine.serializing import XmlLibraryReaderLxml

try:
    reader = XmlLibraryReaderLxml()
    library = reader.read_file("library.xml")
except ImportError:
    print("lxml not installed, install with: pip install lxml")
```

### LibraryReaderFactory

Factory for obtaining readers with automatic service discovery.

**Static Methods:**
- `get_reader(content_type)` - Get reader for content type
- `get_json_reader()` - Get JSON reader
- `get_xml_reader()` - Get XML reader
- `clear_cache()` - Clear reader cache

**Supported Content Types:**
- `"application/elm+json"` - JSON reader
- `"application/elm+xml"` - XML reader
- `"application/json"` - Maps to JSON reader
- `"application/xml"` - Maps to XML reader
- `"text/xml"` - Maps to XML reader
- `None` - Defaults to JSON reader

**Example:**
```python
from cql_engine.serializing import LibraryReaderFactory

# Get reader for specific content type
reader = LibraryReaderFactory.get_reader("application/elm+json")

# Convenience methods
json_reader = LibraryReaderFactory.get_json_reader()
xml_reader = LibraryReaderFactory.get_xml_reader()

# Clear cache if providers change
LibraryReaderFactory.clear_cache()
```

### CqlLibraryReaderProvider (Service Provider Interface)

Interface for service providers that create readers.

**DefaultCqlLibraryReaderProvider:**
The default implementation that provides JSON and XML readers.

**Implementing Custom Providers:**
```python
from cql_engine.serializing import CqlLibraryReaderProvider, CqlLibraryReader

class CustomProvider(CqlLibraryReaderProvider):
    def create(self, content_type: str) -> CqlLibraryReader:
        if content_type == "application/custom":
            return CustomLibraryReader()
        raise ValueError(f"Unsupported type: {content_type}")
```

### LibraryWrapper

Simple wrapper for library objects.

**Methods:**
- `__init__(library)` - Initialize with optional library
- `get_library()` - Get the wrapped library
- `set_library(library)` - Set the library

**Example:**
```python
from cql_engine.serializing import LibraryWrapper, JsonLibraryReader

reader = JsonLibraryReader()
library = reader.read_file("library.json")

wrapper = LibraryWrapper(library)
retrieved = wrapper.get_library()
```

## Error Handling

All readers raise standard Python exceptions:

- `IOError` - For file/URL access issues
- `ValueError` - For malformed JSON/XML content
- `FileNotFoundError` - When specified file doesn't exist
- `TypeError` - For unsupported source types

**Example:**
```python
from cql_engine.serializing import JsonLibraryReader

reader = JsonLibraryReader()

try:
    library = reader.read_file("nonexistent.json")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid JSON: {e}")
except IOError as e:
    print(f"Read error: {e}")
```

## Source Type Support

### Supported Input Types

**File Paths:**
```python
reader.read("/path/to/library.json")
reader.read("library.json")
reader.read(Path("library.json"))
```

**URLs:**
```python
reader.read("https://example.com/library.json")
reader.read("http://example.com/library.xml")
reader.read("ftp://example.com/library.json")
```

**Strings (JSON/XML content):**
```python
json_string = '{"library": {...}}'
reader.read(json_string)

xml_string = '<?xml version="1.0"?><library>...</library>'
reader.read(xml_string)
```

**Binary Streams:**
```python
with open("library.json", "rb") as f:
    reader.read(f)

import io
stream = io.BytesIO(b'{"library": {...}}')
reader.read(stream)
```

**Text Readers:**
```python
import io
text_reader = io.StringIO('{"library": {...}}')
reader.read(text_reader)

with open("library.json", "r") as f:
    reader.read(f)
```

## Migration from Java

### From Jackson JSON Reader
```java
// Java
JsonCqlLibraryReader reader = new JsonCqlLibraryReader();
Library library = reader.read(file);
```

```python
# Python
from cql_engine.serializing import JsonLibraryReader

reader = JsonLibraryReader()
library = reader.read(file)
```

### From JAXB XML Reader
```java
// Java
XmlCqlLibraryReader reader = new XmlCqlLibraryReader();
Library library = reader.read(file);
```

```python
# Python
from cql_engine.serializing import XmlLibraryReader

reader = XmlLibraryReader()
library = reader.read(file)
```

### From CqlLibraryReaderFactory
```java
// Java
CqlLibraryReaderFactory factory = new CqlLibraryReaderFactory();
CqlLibraryReader reader = factory.create("application/elm+json");
Library library = reader.read(file);
```

```python
# Python
from cql_engine.serializing import LibraryReaderFactory

reader = LibraryReaderFactory.get_reader("application/elm+json")
library = reader.read(file)
```

## Performance Considerations

1. **Reader Caching**: LibraryReaderFactory caches reader instances by content type
2. **Stream Efficiency**: Reading from streams is more memory-efficient than loading entire files
3. **XML Parsing**: Use XmlLibraryReaderLxml for large files if lxml is available
4. **URL Fetching**: Consider caching remote libraries locally for better performance

## Testing

Example test cases:

```python
import unittest
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from cql_engine.serializing import JsonLibraryReader, XmlLibraryReader, LibraryReaderFactory

class TestLibraryReaders(unittest.TestCase):
    def test_json_reader_from_file(self):
        reader = JsonLibraryReader()
        library = reader.read_file("test_library.json")
        self.assertIsNotNone(library)

    def test_json_reader_from_string(self):
        json_str = '{"library": {"name": "Test"}}'
        reader = JsonLibraryReader()
        library = reader.read_string(json_str)
        self.assertEqual(library["library"]["name"], "Test")

    def test_xml_reader_from_string(self):
        xml_str = '<?xml version="1.0"?><library><name>Test</name></library>'
        reader = XmlLibraryReader()
        library = reader.read_string(xml_str)
        self.assertEqual(library["_tag"], "library")

    def test_factory_get_json_reader(self):
        reader = LibraryReaderFactory.get_json_reader()
        self.assertIsNotNone(reader)

    def test_factory_get_xml_reader(self):
        reader = LibraryReaderFactory.get_xml_reader()
        self.assertIsNotNone(reader)
```

## License

Same as the CQL Engine project
