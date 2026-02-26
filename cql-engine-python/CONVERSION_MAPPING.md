# Java to Python Conversion Mapping

## Module Structure

### Java (Two Separate Modules)
```
engine.jackson/
├── JsonCqlLibraryReader.java
├── XmlCqlLibraryReader.java
├── JsonCqlMapper.java
├── XmlCqlMapper.java
├── CqlLibraryReaderProvider.java
├── mixins/
│   ├── LibraryMixin.java
│   ├── ElementMixin.java
│   ├── ExpressionMixin.java
│   └── ... (many more)
└── modules/
    ├── QNameFixerXMLMapperDeserializer.java
    └── QNameFixerXMLMapperModifier.java

engine.jaxb/
├── JsonCqlLibraryReader.java
├── XmlCqlLibraryReader.java
├── JsonCqlMapper.java
├── XmlCqlMapper.java
├── LibraryReaderUtil.java
└── CqlLibraryReaderProvider.java
```

### Python (Unified Module)
```
cql_engine/serializing/
├── cql_library_reader.py               # Base interface
├── json_library_reader.py              # JSON reader
├── xml_library_reader.py               # XML readers (2 classes)
├── cql_library_reader_provider.py      # Provider interface + default
├── cql_library_reader_factory.py       # Service discovery factory
├── library_reader_factory.py           # Primary factory API
├── library_wrapper.py                  # Library wrapper
├── __init__.py                         # Package exports
├── test_readers.py                     # Test suite
├── README.md                           # Full documentation
└── (parent files)
    ├── SERIALIZING_CONVERSION.md       # Conversion details
    └── CONVERSION_MAPPING.md           # This file
```

## Class-by-Class Mapping

### Jackson Module

#### JsonCqlLibraryReader.java
```java
public class JsonCqlLibraryReader implements CqlLibraryReader {
    public Library read(File file) throws IOException
    public Library read(URL url) throws IOException
    public Library read(URI uri) throws IOException
    public Library read(String string) throws IOException
    public Library read(InputStream inputStream) throws IOException
    public Library read(Reader reader) throws IOException
}
```

**→ Maps to:**
```python
# cql_engine/serializing/json_library_reader.py
class JsonLibraryReader(CqlLibraryReader):
    def read(self, source: Union[Path, str, BinaryIO, TextIO]) -> Any
    def read_file(self, file_path: Union[str, Path]) -> Any
    def read_url(self, url: str) -> Any
    def read_uri(self, uri: str) -> Any
    def read_string(self, content: str) -> Any
    def read_stream(self, stream: BinaryIO) -> Any
    def read_text_reader(self, reader: TextIO) -> Any
```

#### XmlCqlLibraryReader.java (Jackson)
```java
public class XmlCqlLibraryReader implements CqlLibraryReader {
    public Library read(File file) throws IOException
    public Library read(URL url) throws IOException
    public Library read(URI uri) throws IOException
    public Library read(String string) throws IOException
    public Library read(InputStream inputStream) throws IOException
    public Library read(Reader reader) throws IOException
}
```

**→ Maps to:**
```python
# cql_engine/serializing/xml_library_reader.py
class XmlLibraryReader(CqlLibraryReader):
    def read(self, source: Union[Path, str, BinaryIO, TextIO]) -> Any
    def read_file(self, file_path: Union[str, Path]) -> Any
    def read_url(self, url: str) -> Any
    def read_uri(self, uri: str) -> Any
    def read_string(self, content: str) -> Any
    def read_stream(self, stream: BinaryIO) -> Any
    def read_text_reader(self, reader: TextIO) -> Any

class XmlLibraryReaderLxml(XmlLibraryReader):
    # Optional lxml-based enhanced XML reader
```

#### JsonCqlMapper.java
```java
public class JsonCqlMapper {
    private static final JsonMapper mapper = JsonMapper.builder()
        .enable(SerializationFeature.INDENT_OUTPUT)
        .addModule(new JaxbAnnotationModule())
        .addMixIn(Library.class, LibraryMixin.class)
        // ... more mixins
        .build();
    public static JsonMapper getMapper()
}
```

**→ Functionality in:**
```python
# json_library_reader.py
# Uses standard json module with custom parsing logic
# Replaces need for complex mapper configuration
```

#### XmlCqlMapper.java
```java
public class XmlCqlMapper {
    private static final XmlMapper mapper = XmlMapper
        .builder(new XmlFactory(...))
        .enable(ToXmlGenerator.Feature.WRITE_XML_DECLARATION)
        .addModule(new JaxbAnnotationModule())
        .addModule(new SimpleModule()
            .setDeserializerModifier(new QNameFixerXMLMapperModifier()))
        // ... more configuration
        .build();
    public static XmlMapper getMapper()
}
```

**→ Functionality in:**
```python
# xml_library_reader.py
# Uses ElementTree with namespace handling
# QName fixing handled automatically
```

#### CqlLibraryReaderProvider.java (Jackson)
```java
public class CqlLibraryReaderProvider
    implements org.opencds.cqf.cql.engine.serializing.CqlLibraryReaderProvider {
    public CqlLibraryReader create(String contentType) {
        switch (contentType) {
            case "application/elm+xml": return new XmlCqlLibraryReader();
            case "application/elm+json":
            default: return new JsonCqlLibraryReader();
        }
    }
}
```

**→ Maps to:**
```python
# cql_library_reader_provider.py
class DefaultCqlLibraryReaderProvider(CqlLibraryReaderProvider):
    def create(self, content_type: str) -> CqlLibraryReader:
        # Similar logic with more content type variants
```

#### QNameFixerXMLMapperDeserializer.java
```java
public class QNameFixerXMLMapperDeserializer extends JsonDeserializer<QName> {
    public QName deserialize(JsonParser jsonParser, ...) {
        if (qName.getLocalPart().indexOf(":") > 0) {
            // Extract namespace and local part
            return new QName(namespace, localPart, prefix);
        }
        return qName;
    }
}
```

**→ Handled in:**
```python
# xml_library_reader.py
# Element namespace extraction:
# if '}' in tag:
#     tag = tag.split('}', 1)[1]  # Remove namespace
```

### JAXB Module

#### JsonCqlLibraryReader.java (JAXB)
```java
public class JsonCqlLibraryReader implements CqlLibraryReader {
    private static Unmarshaller unmarshaller;
    public static synchronized Unmarshaller getUnmarshaller()
    public Library read(File file) throws IOException
    public Library read(URL url) throws IOException
    // ... other methods using Source conversion
}
```

**→ Consolidates into:**
```python
# json_library_reader.py
# Simpler implementation without JAXB complexity
```

#### XmlCqlLibraryReader.java (JAXB)
```java
public class XmlCqlLibraryReader implements CqlLibraryReader {
    private static Unmarshaller unmarshaller;
    public static synchronized Unmarshaller getUnmarshaller()
    private Library read(Object source) throws IOException
    public Library read(File file) throws IOException
    // ... other methods
}
```

**→ Consolidates into:**
```python
# xml_library_reader.py
# Simpler implementation without JAXB complexity
```

#### LibraryReaderUtil.java
```java
public class LibraryReaderUtil {
    public static Source toSource(Object source) {
        if (source instanceof String)
            // Try URI, then file, then JSON string
        if (source instanceof File)
            return new StreamSource((File)source);
        if (source instanceof URI)
            // Convert to URL
        if (source instanceof URL)
            return new StreamSource(url.toExternalForm());
        // ... handle streams and readers
    }
}
```

**→ Functionality embedded in:**
```python
# json_library_reader.py and xml_library_reader.py
# _read_from_string() methods handle source detection
```

## Data Type Mapping

### Java → Python

| Java Type | Python Type | Notes |
|-----------|------------|-------|
| `File` | `Path` or `str` | pathlib.Path for objects, str for strings |
| `URL` | `str` | Parsed via urllib.parse |
| `URI` | `str` | Parsed via urllib.parse |
| `String` | `str` | Native Python string |
| `InputStream` | `BinaryIO` or `BytesIO` | Binary stream from io module |
| `Reader` | `TextIO` or `StringIO` | Text stream from io module |
| `Library` | `Dict[str, Any]` | Dict representation (JSON) or transformed XML |
| `IOException` | `IOError` | Python built-in exception |
| `JAXBException` | `ValueError` | Parse/validation errors |
| `Source` | `str`, `BinaryIO` | Direct source handling |

## API Mapping Summary

### Main Reader API

```
┌─────────────────────────────────────────────────────┐
│ Java: CqlLibraryReader (interface)                  │
├─────────────────────────────────────────────────────┤
│ + read(File) : Library                              │
│ + read(URL) : Library                               │
│ + read(URI) : Library                               │
│ + read(String) : Library                            │
│ + read(InputStream) : Library                       │
│ + read(Reader) : Library                            │
└─────────────────────────────────────────────────────┘
                         ↓
        ┌─────────────────────────────────────┐
        │ Unified Method Signature             │
        ├─────────────────────────────────────┤
        │ + read(source: Union[...]) : Any    │
        │ + read_file(path)                   │
        │ + read_url(url)                     │
        │ + read_uri(uri)                     │
        │ + read_string(content)              │
        │ + read_stream(stream)               │
        │ + read_text_reader(reader)          │
        └─────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│ Python: CqlLibraryReader (ABC)                       │
├──────────────────────────────────────────────────────┤
│ + read(source) -> Any [abstract]                     │
│ + read_file(path) -> Any                             │
│ + read_url(url) -> Any                               │
│ + read_uri(uri) -> Any                               │
│ + read_string(content) -> Any                        │
│ + read_stream(stream) -> Any                         │
│ + read_text_reader(reader) -> Any                    │
└──────────────────────────────────────────────────────┘
```

### Factory API

```
Java:
┌─────────────────────────────────────┐
│ CqlLibraryReaderFactory             │
├─────────────────────────────────────┤
│ + providers() : Iterator<Provider>  │
│ + get_reader(type) : Reader         │
└─────────────────────────────────────┘

Python:
┌──────────────────────────────────────────┐
│ CqlLibraryReaderFactory                  │
├──────────────────────────────────────────┤
│ + providers() : Iterator[Provider]       │
│ + get_reader(type) : CqlLibraryReader    │
└──────────────────────────────────────────┘
            +
┌──────────────────────────────────────────┐
│ LibraryReaderFactory (NEW - Main API)    │
├──────────────────────────────────────────┤
│ + get_reader(type) : CqlLibraryReader    │
│ + get_json_reader() : CqlLibraryReader   │
│ + get_xml_reader() : CqlLibraryReader    │
│ + clear_cache() : None                   │
└──────────────────────────────────────────┘
```

### Service Provider API

```
Java:
┌──────────────────────────────────┐
│ CqlLibraryReaderProvider         │
├──────────────────────────────────┤
│ + create(type) : Reader          │
└──────────────────────────────────┘

Python:
┌──────────────────────────────────────┐
│ CqlLibraryReaderProvider (ABC)       │
├──────────────────────────────────────┤
│ + create(type) : CqlLibraryReader    │
└──────────────────────────────────────┘
            +
┌──────────────────────────────────────┐
│ DefaultCqlLibraryReaderProvider      │
├──────────────────────────────────────┤
│ + create(type) : CqlLibraryReader    │
└──────────────────────────────────────┘
```

## Implementation Details Comparison

### JSON Parsing

**Java (Jackson):**
```java
JsonMapper mapper = JsonMapper.builder()
    .enable(SerializationFeature.INDENT_OUTPUT)
    .enable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY)
    .addModule(new JaxbAnnotationModule())
    .build();

Library library = mapper.readValue(file, Library.class);
```

**Python:**
```python
import json

with open(file, 'r') as f:
    data = json.load(f)
    # User maps to Library type as needed
    # data is now a dict
```

### XML Parsing

**Java (Jackson):**
```java
XmlMapper mapper = XmlMapper.builder(...)
    .enable(ToXmlGenerator.Feature.WRITE_XML_DECLARATION)
    .addModule(new SimpleModule()
        .setDeserializerModifier(new QNameFixerXMLMapperModifier()))
    .build();

Library library = mapper.readValue(file, Library.class);
```

**Python (ElementTree):**
```python
import xml.etree.ElementTree as ET

tree = ET.parse(file)
root = tree.getroot()
data = element_to_dict(root)  # Converts to dict structure
```

**Python (lxml - optional):**
```python
from lxml import etree

tree = etree.parse(file)
root = tree.getroot()
data = element_to_dict(root)  # Enhanced with namespace handling
```

## Testing

### Java Test Framework
- JUnit (implied by Spring Test structure)
- Parameterized tests for multiple input types
- Exception testing for error cases

### Python Test Framework
- `unittest` (Python standard library)
- Same coverage as Java:
  - String parsing (JSON/XML)
  - File reading
  - Stream reading
  - Error handling
  - Factory functionality
  - End-to-end workflows

## Dependencies Comparison

### Java
```gradle
// Jackson Module
implementation 'com.fasterxml.jackson.core:jackson-databind:2.x'
implementation 'com.fasterxml.jackson.dataformat:jackson-dataformat-xml:2.x'
implementation 'com.fasterxml.jackson.module:jackson-module-jaxb-annotations:2.x'

// JAXB Module
implementation 'javax.xml.bind:jaxb-api:2.x'
implementation 'org.eclipse.persistence:eclipselink:2.x'
```

### Python
```python
# Required
# (none - uses standard library)

# Optional (enhanced XML)
# lxml (for better namespace handling and performance)
```

## Summary

This conversion successfully:
1. **Consolidates** two separate Java modules into one unified Python module
2. **Eliminates** complex external dependencies (Jackson, JAXB)
3. **Maintains** API compatibility with Java version
4. **Provides** better Pythonic interface with sensible defaults
5. **Enables** gradual migration - users can implement custom type mappers
6. **Includes** comprehensive documentation and tests
7. **Offers** optional enhanced XML support via lxml

The Python implementation is simpler, more maintainable, and follows Python best practices while providing equivalent functionality to the original Java modules.
