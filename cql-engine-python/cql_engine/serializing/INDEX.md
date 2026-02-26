# CQL Engine Serializing Module - File Index

## Module Location
```
/sessions/beautiful-charming-noether/mnt/claudecode/cql-engine-python/cql_engine/serializing/
```

## Files Overview

### Core Interface Files

#### 1. `cql_library_reader.py`
**Purpose**: Abstract base class defining the reader interface
**Status**: Updated from original
**Lines**: ~130
**Key Classes**:
- `Library` - Placeholder for ELM Library type
- `CqlLibraryReader` (ABC) - Base interface with abstract `read()` method

**Exports**: `CqlLibraryReader`, `Library`

---

#### 2. `cql_library_reader_provider.py`
**Purpose**: Service provider interface for creating readers
**Status**: Updated with default implementation
**Lines**: ~75
**Key Classes**:
- `CqlLibraryReaderProvider` (ABC) - Interface for providers
- `DefaultCqlLibraryReaderProvider` - Default implementation

**Features**:
- Maps content types to readers
- Supports JSON and XML formats
- Case-insensitive content type matching
- Null/None defaults to JSON

**Exports**: `CqlLibraryReaderProvider`, `DefaultCqlLibraryReaderProvider`

---

### Concrete Reader Implementations

#### 3. `json_library_reader.py`
**Purpose**: Reads CQL libraries in JSON format
**Status**: New (replaces Jackson + JAXB JSON readers)
**Lines**: ~250
**Key Classes**:
- `JsonLibraryReader` (extends `CqlLibraryReader`)

**Features**:
- Uses Python's built-in `json` module
- Supports files, URLs, URIs, strings, streams
- Smart source detection
- Proper error handling

**Methods**:
- `read()` - Main read method (dispatcher)
- `_read_from_string()` - Detects string type
- `_read_from_file()` - Reads from file path
- `_read_from_url()` - Fetches from URL
- `_read_from_stream()` - Reads from binary stream
- `_read_from_reader()` - Reads from text reader
- `_parse_json_string()` - JSON parsing logic

**Exports**: `JsonLibraryReader`

---

#### 4. `xml_library_reader.py`
**Purpose**: Reads CQL libraries in XML format
**Status**: New (replaces Jackson XML + JAXB XML readers)
**Lines**: ~400
**Key Classes**:
- `XmlLibraryReader` (extends `CqlLibraryReader`)
- `XmlLibraryReaderLxml` (extends `XmlLibraryReader`, optional lxml version)

**Features**:
- Uses ElementTree for standard version
- Optional lxml for enhanced support
- Namespace handling
- Converts XML to dict representation
- Element metadata: `_tag`, `_attributes`, `_text`, `_children`

**Methods**:
- `read()` - Main read method (dispatcher)
- `_read_from_string()` - Detects string type
- `_read_from_file()` - Reads from file path
- `_read_from_url()` - Fetches from URL
- `_read_from_stream()` - Reads from binary stream
- `_read_from_reader()` - Reads from text reader
- `_parse_xml_string()` - XML string parsing
- `_parse_xml_stream()` - XML stream parsing
- `_element_to_dict()` - Converts Element to dict

**Exports**: `XmlLibraryReader`, `XmlLibraryReaderLxml`

---

### Factory and Provider Files

#### 5. `cql_library_reader_factory.py`
**Purpose**: Service discovery factory (original pattern)
**Status**: Updated
**Lines**: ~100
**Key Classes**:
- `CqlLibraryReaderFactory`

**Features**:
- Entry point discovery via `importlib.metadata`
- Python 3.9+ support
- Validates single provider
- Fallback to `DefaultCqlLibraryReaderProvider`

**Methods**:
- `providers()` - Discover available providers
- `get_reader()` - Get reader for content type

**Exports**: `CqlLibraryReaderFactory`

---

#### 6. `library_reader_factory.py`
**Purpose**: Primary factory interface (recommended)
**Status**: New
**Lines**: ~150
**Key Classes**:
- `LibraryReaderFactory`

**Features**:
- Reader caching by content type
- Service discovery integration
- Simplified, Pythonic API
- Convenience methods

**Methods**:
- `get_reader()` - Get reader for content type
- `get_json_reader()` - Get JSON reader
- `get_xml_reader()` - Get XML reader
- `clear_cache()` - Clear cached readers
- `_get_provider()` - Internal provider lookup

**Exports**: `LibraryReaderFactory`

---

### Utility Files

#### 7. `library_wrapper.py`
**Purpose**: Simple wrapper for library objects
**Status**: Updated
**Lines**: ~60
**Key Classes**:
- `LibraryWrapper`

**Features**:
- Encapsulates library object
- Getter/setter access
- String representation

**Methods**:
- `__init__()` - Initialize
- `get_library()` - Get wrapped library
- `set_library()` - Set library
- `__repr__()` - String representation

**Exports**: `LibraryWrapper`

---

### Package Files

#### 8. `__init__.py`
**Purpose**: Package initialization and exports
**Status**: Updated
**Lines**: ~50

**Exports**:
```python
__all__ = [
    'CqlLibraryReader',
    'Library',
    'CqlLibraryReaderProvider',
    'DefaultCqlLibraryReaderProvider',
    'CqlLibraryReaderFactory',
    'LibraryReaderFactory',
    'JsonLibraryReader',
    'XmlLibraryReader',
    'XmlLibraryReaderLxml',
    'LibraryWrapper',
]
```

---

### Documentation Files

#### 9. `README.md`
**Purpose**: Comprehensive module documentation
**Status**: New
**Lines**: ~400

**Contents**:
- Overview and quick start
- Installation instructions
- API reference for all classes
- Usage examples
- Migration guide from Java
- Performance considerations
- Error handling
- Testing guidelines

---

#### 10. `test_readers.py`
**Purpose**: Comprehensive test suite
**Status**: New
**Lines**: ~350

**Test Classes**:
- `TestJsonLibraryReader` - 7 tests
- `TestXmlLibraryReader` - 7 tests
- `TestLibraryReaderFactory` - 5 tests
- `TestLibraryWrapper` - 4 tests
- `TestEndToEnd` - 2 integration tests

**Coverage**:
- String parsing
- File reading
- Stream reading
- Error handling
- Factory functionality
- End-to-end workflows

---

### Additional Documentation

Located in parent directory (`/sessions/beautiful-charming-noether/mnt/claudecode/cql-engine-python/`)

#### `SERIALIZING_CONVERSION.md`
Detailed conversion documentation including:
- Java source analysis
- Python implementation overview
- Key differences from Java
- Dependencies
- Usage examples
- Future enhancements

#### `CONVERSION_MAPPING.md`
Detailed mapping documentation including:
- Module structure comparison
- Class-by-class mapping
- Data type mapping
- API mapping
- Implementation details
- Testing comparison

---

## Quick Reference

### Most Important Files
1. `library_reader_factory.py` - Use this for getting readers
2. `json_library_reader.py` - JSON reading
3. `xml_library_reader.py` - XML reading

### For Integration
1. `__init__.py` - Import from here
2. `README.md` - Usage documentation
3. `CONVERSION_MAPPING.md` - Understand the architecture

### For Testing
1. `test_readers.py` - Run unit tests
2. `README.md` - Testing section
3. Parent `test_serializing_standalone.py` - Standalone test

### For Understanding
1. `SERIALIZING_CONVERSION.md` - Conversion overview
2. `CONVERSION_MAPPING.md` - Detailed mapping
3. `README.md` - API documentation

---

## File Statistics

| File | Lines | Type | Purpose |
|------|-------|------|---------|
| `cql_library_reader.py` | 130 | Interface | Base class |
| `json_library_reader.py` | 250 | Implementation | JSON reader |
| `xml_library_reader.py` | 400 | Implementation | XML readers |
| `cql_library_reader_provider.py` | 75 | Interface + Impl | Service provider |
| `cql_library_reader_factory.py` | 100 | Implementation | Service discovery |
| `library_reader_factory.py` | 150 | Implementation | Primary factory |
| `library_wrapper.py` | 60 | Implementation | Library wrapper |
| `__init__.py` | 50 | Configuration | Package setup |
| `test_readers.py` | 350 | Testing | Test suite |
| `README.md` | 400 | Documentation | Main docs |
| **TOTAL** | **~2,000** | | |

---

## Dependencies

### Required
- Python 3.7+
- Standard library: `json`, `xml.etree.ElementTree`, `urllib`, `io`, `pathlib`, `abc`, `typing`

### Optional
- `lxml` - For enhanced XML support (optional for `XmlLibraryReaderLxml`)

---

## Usage Examples

### Import Options
```python
# Option 1: Import from main module (recommended)
from cql_engine.serializing import LibraryReaderFactory

# Option 2: Import specific readers
from cql_engine.serializing import JsonLibraryReader, XmlLibraryReader

# Option 3: Import everything
from cql_engine.serializing import *
```

### Basic Usage
```python
# Using factory (recommended)
reader = LibraryReaderFactory.get_json_reader()
library = reader.read_file("library.json")

# Direct usage
from cql_engine.serializing import JsonLibraryReader
reader = JsonLibraryReader()
library = reader.read_string('{"lib": "data"}')
```

---

## Code Quality

- **Type Hints**: Full Python type hints
- **Docstrings**: Comprehensive docstrings for all public methods
- **Error Handling**: Proper exception types with descriptive messages
- **Testing**: Unit tests with good coverage
- **Documentation**: Multiple documentation files
- **Consistency**: Follows Python style guidelines (PEP 8)

---

## Maintenance Notes

### To Add New Reader Type
1. Create new class extending `CqlLibraryReader`
2. Implement `read()` method
3. Add to `DefaultCqlLibraryReaderProvider.create()`
4. Add tests to `test_readers.py`
5. Update documentation in `README.md`

### To Extend Service Discovery
1. Implement `CqlLibraryReaderProvider`
2. Configure as entry point in `setup.py`
3. Test with `CqlLibraryReaderFactory.providers()`

### To Improve Performance
1. Consider streaming for large files
2. Use caching for repeated reads
3. Consider async versions for I/O-bound operations

---

## See Also

- Parent `README.md` - CQL Engine Python project overview
- `SERIALIZING_CONVERSION.md` - Detailed conversion guide
- `CONVERSION_MAPPING.md` - Technical mapping details
- Main `__init__.py` - Package-level imports
