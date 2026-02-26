# CQL Engine Serialization Module Conversion: Java to Python

## Overview

This document describes the conversion of the CQL Engine serialization modules (Jackson and JAXB) from Java to modern Python. The conversion consolidates both separate Java modules into a single, unified Python module using Python's standard library and optional dependencies.

## Java Source Analysis

### Jackson Module Source Files
Located in: `/tmp/cql-engine/engine.jackson/src/main/java/`

Key files analyzed:
- `JsonCqlLibraryReader.java` - Reads JSON format CQL libraries
- `XmlCqlLibraryReader.java` - Reads XML format using Jackson XML mapper
- `JsonCqlMapper.java` - Jackson mapper configuration for JSON
- `XmlCqlMapper.java` - Jackson mapper configuration for XML
- `CqlLibraryReaderProvider.java` - Service provider for reader creation
- Various Mixins - Type mapping and serialization customizations

### JAXB Module Source Files
Located in: `/tmp/cql-engine/engine.jaxb/src/main/java/`

Key files analyzed:
- `JsonCqlLibraryReader.java` - JAXB-based JSON reader
- `XmlCqlLibraryReader.java` - JAXB-based XML reader
- `JsonCqlMapper.java` - JAXB context configuration
- `XmlCqlMapper.java` - JAXB context configuration
- `LibraryReaderUtil.java` - Source conversion utilities
- `CqlLibraryReaderProvider.java` - Service provider

## Python Implementation

### Created Files

All files are located in: `/sessions/beautiful-charming-noether/mnt/claudecode/cql-engine-python/cql_engine/serializing/`

#### 1. **cql_library_reader.py** (Updated)
- **Purpose**: Abstract base class for all library readers
- **Replaces**: Java `CqlLibraryReader` interface
- **Key Methods**:
  - `read(source)` - Abstract method for reading from various sources
  - `read_file(file_path)` - Read from file
  - `read_url(url)` - Read from URL
  - `read_uri(uri)` - Read from URI (file or URL)
  - `read_string(content)` - Read from string
  - `read_stream(stream)` - Read from binary stream
  - `read_text_reader(reader)` - Read from text reader
- **Notes**: Updated with better documentation and type hints

#### 2. **json_library_reader.py** (New)
- **Purpose**: Reads CQL libraries in JSON format
- **Replaces**:
  - Jackson's `JsonCqlLibraryReader.java`
  - JAXB's `JsonCqlLibraryReader.java`
- **Implementation Details**:
  - Uses Python's built-in `json` module (no external dependencies)
  - Handles multiple input types: files, URLs, URIs, strings, streams
  - Smart source detection (tries URL → file → JSON string)
  - Proper error handling with detailed messages
- **Key Features**:
  - File path recognition (string vs. file path vs. JSON)
  - URL/URI handling with `urllib.request`
  - Stream and reader support
  - Caching of read results in internal state

#### 3. **xml_library_reader.py** (New)
- **Purpose**: Reads CQL libraries in XML format
- **Replaces**:
  - Jackson's `XmlCqlLibraryReader.java` with XML mapper
  - JAXB's `XmlCqlLibraryReader.java`
  - Jackson's namespace handling fixes
- **Implementation Details**:
  - Uses Python's `xml.etree.ElementTree` for standard version
  - Converts XML to Python dict representation
  - Handles namespaces properly
  - Element-to-dict conversion with metadata
- **Key Classes**:
  - `XmlLibraryReader` - Standard ElementTree-based reader
  - `XmlLibraryReaderLxml` - Optional lxml-based reader for enhanced XML support
- **XML Conversion Structure**:
  - `_tag` - Element tag name (without namespace)
  - `_attributes` - Dictionary of element attributes
  - `_text` - Text content
  - `_children` - Dictionary of child elements (lists for multiples)

#### 4. **cql_library_reader_provider.py** (Updated)
- **Purpose**: Service provider interface for reader creation
- **Replaces**: Java `CqlLibraryReaderProvider` interface
- **New Implementation**: `DefaultCqlLibraryReaderProvider`
  - Maps content types to appropriate readers:
    - `application/elm+json`, `application/json` → JsonLibraryReader
    - `application/elm+xml`, `application/xml`, `text/xml` → XmlLibraryReader
  - Case-insensitive content type matching
  - None/null defaults to JSON

#### 5. **cql_library_reader_factory.py** (Updated)
- **Purpose**: Service discovery factory (original factory pattern)
- **Replaces**: Java `CqlLibraryReaderFactory.get_reader()`
- **Enhanced Features**:
  - Entry point discovery via `importlib.metadata`
  - Fallback to `DefaultCqlLibraryReaderProvider`
  - Provider validation (ensure only one provider)
  - Works with Python 3.9+ entry points

#### 6. **library_reader_factory.py** (New)
- **Purpose**: Primary factory interface (recommended way to get readers)
- **Replaces**: Java `CqlLibraryReaderFactory` (simplified API)
- **Key Methods**:
  - `get_reader(content_type)` - Get reader for specific content type
  - `get_json_reader()` - Convenience method for JSON
  - `get_xml_reader()` - Convenience method for XML
  - `clear_cache()` - Clear cached readers
- **Features**:
  - Reader caching by content type
  - Service discovery via `CqlLibraryReaderFactory`
  - Simplified, Pythonic API

#### 7. **library_wrapper.py** (Updated)
- **Purpose**: Simple wrapper for library objects
- **Replaces**: Implicit Java wrapper functionality
- **Key Methods**:
  - `__init__(library)` - Initialize with optional library
  - `get_library()` - Get wrapped library
  - `set_library(library)` - Set library
- **Enhancements**:
  - Improved documentation
  - String representation via `__repr__`

#### 8. **__init__.py** (Updated)
- **Purpose**: Package exports and API
- **Exports**:
  - Core interfaces: `CqlLibraryReader`, `Library`
  - Providers: `CqlLibraryReaderProvider`, `DefaultCqlLibraryReaderProvider`
  - Factories: `CqlLibraryReaderFactory`, `LibraryReaderFactory`
  - Readers: `JsonLibraryReader`, `XmlLibraryReader`, `XmlLibraryReaderLxml`
  - Wrapper: `LibraryWrapper`

#### 9. **test_readers.py** (New)
- Comprehensive test suite with unittest framework
- Tests for:
  - JSON reading (string, file, stream, errors)
  - XML reading (string, file, stream, attributes, children)
  - Factory functionality and caching
  - LibraryWrapper operations
  - End-to-end workflows
  - Error handling

#### 10. **README.md** (New)
- Comprehensive documentation including:
  - Module overview and architecture
  - Installation instructions
  - Quick start examples
  - API reference for all classes
  - Usage patterns and examples
  - Migration guide from Java
  - Performance considerations
  - Testing guidelines

## Key Differences from Java Implementation

### 1. **Unified Module**
- Java: Separate Jackson and JAXB modules with service discovery
- Python: Single unified module with pluggable providers

### 2. **Data Structure**
- Java: Uses Jackson/JAXB to deserialize directly to typed Java objects
- Python: Deserializes to dict-like structures (more Pythonic)
  - Users can map to typed classes as needed

### 3. **Error Handling**
- Java: Throws checked exceptions (IOException, JAXBException)
- Python: Raises IOError for file/stream issues, ValueError for parse errors

### 4. **Dependencies**
- Jackson: Uses Jackson libraries for all mapping
- JAXB: Uses JAXB and EclipseLink
- Python JSON: Uses standard `json` module (no external deps)
- Python XML: Uses standard `xml.etree.ElementTree` (no external deps)
- Python XML (optional): Can use `lxml` for enhanced features

### 5. **QName Handling**
- Java: Custom deserializer `QNameFixerXMLMapperDeserializer` to fix namespace issues
- Python: Standard namespace handling in ElementTree, exposed in element dict

### 6. **Mixins and Type Mapping**
- Java: Uses complex mixin system with type mapping
- Python: Simple type detection based on content-type header or file extension

## Dependencies

### Required
- Python 3.7+
- Standard library only: `json`, `xml.etree.ElementTree`, `urllib`, `io`, `pathlib`

### Optional
- `lxml` - For enhanced XML support (install with `pip install lxml`)

## Usage Examples

### Basic JSON Reading
```python
from cql_engine.serializing import JsonLibraryReader

reader = JsonLibraryReader()
library = reader.read_file("path/to/library.json")
```

### Basic XML Reading
```python
from cql_engine.serializing import XmlLibraryReader

reader = XmlLibraryReader()
library = reader.read_file("path/to/library.xml")
```

### Using Factory (Recommended)
```python
from cql_engine.serializing import LibraryReaderFactory

# Auto-detect based on content type
reader = LibraryReaderFactory.get_reader("application/elm+json")
library = reader.read_file("library.json")

# Convenience methods
json_reader = LibraryReaderFactory.get_json_reader()
xml_reader = LibraryReaderFactory.get_xml_reader()
```

### With Wrapper
```python
from cql_engine.serializing import LibraryReaderFactory, LibraryWrapper

reader = LibraryReaderFactory.get_json_reader()
library = reader.read_file("library.json")
wrapper = LibraryWrapper(library)

# Access library
wrapped_lib = wrapper.get_library()
```

## Testing

Run the test suite:
```bash
cd /sessions/beautiful-charming-noether/mnt/claudecode/cql-engine-python
python -m unittest cql_engine.serializing.test_readers -v
```

Or run the standalone test:
```bash
python test_serializing_standalone.py
```

## Supported Content Types

| Content Type | Reader |
|---|---|
| `application/elm+json` | JsonLibraryReader |
| `application/elm+xml` | XmlLibraryReader |
| `application/json` | JsonLibraryReader |
| `application/xml` | XmlLibraryReader |
| `text/xml` | XmlLibraryReader |
| `None` (default) | JsonLibraryReader |

## File Locations

All files are created in:
```
/sessions/beautiful-charming-noether/mnt/claudecode/cql-engine-python/cql_engine/serializing/
```

- Core interface: `cql_library_reader.py`
- JSON reader: `json_library_reader.py`
- XML readers: `xml_library_reader.py` (2 classes)
- Providers: `cql_library_reader_provider.py`
- Factories: `cql_library_reader_factory.py`, `library_reader_factory.py`
- Wrapper: `library_wrapper.py`
- Package init: `__init__.py`
- Documentation: `README.md`
- Tests: `test_readers.py`

## Future Enhancements

1. **Type Mapping**: Create mapper classes to convert dict structures to typed Library objects
2. **Caching**: Add library caching layer for performance
3. **Validation**: Add XML/JSON schema validation
4. **Streaming**: Add streaming parser for large files
5. **Async Support**: Add async versions of readers
6. **Custom Serializers**: Support custom deserialization rules

## Conclusion

This Python implementation successfully converts the Java Jackson and JAXB modules into a modern, Pythonic interface that:
- Maintains API compatibility with Java version
- Eliminates external dependencies for core JSON/XML support
- Provides extensibility through service providers
- Includes comprehensive documentation and tests
- Follows Python best practices and conventions
