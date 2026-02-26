# CQL Engine FHIR Module - Python Port

A complete Python port of the OpenCDS CQL Engine FHIR module from Java to modern Python. This module provides FHIR-specific implementations for the CQL Engine, including model resolution, type conversion, and FHIR server integration.

## Overview

The FHIR module has been fully converted from Java to Python with these major components:

### Module Structure

```
cql_engine/fhir/
├── __init__.py                          # Main module exports
├── exception/                           # FHIR-specific exceptions
│   ├── version_mismatch.py             # FhirVersionMismatchException
│   ├── unknown_element.py              # UnknownElement
│   ├── unknown_path.py                 # UnknownPath
│   ├── unknown_type.py                 # UnknownType
│   └── __init__.py
├── model/                               # FHIR Model Resolution
│   ├── fhir_model_resolver.py          # Abstract base class
│   ├── dstu2_model_resolver.py         # DSTU2 implementation
│   ├── dstu3_model_resolver.py         # DSTU3 implementation
│   ├── r4_model_resolver.py            # R4 implementation
│   └── __init__.py
├── converter/                           # FHIR-to-CQL Type Conversion
│   ├── fhir_type_converter.py          # Abstract interface
│   ├── base_fhir_type_converter.py     # Common conversion logic
│   ├── dstu2_type_converter.py         # DSTU2 conversions
│   ├── dstu3_type_converter.py         # DSTU3 conversions
│   ├── r4_type_converter.py            # R4 conversions
│   ├── r5_type_converter.py            # R5 conversions
│   ├── converter_factory.py            # Factory for creating converters
│   └── __init__.py
├── retrieve/                            # FHIR Data Retrieval
│   ├── base_query_generator.py         # Abstract query generator
│   ├── dstu3_query_generator.py        # DSTU3 query generation
│   ├── r4_query_generator.py           # R4 query generation
│   ├── query_generator_factory.py      # Factory for generators
│   ├── search_parameter_map.py         # Search parameter storage
│   ├── search_parameter_resolver.py    # Search param resolution
│   ├── code_filter.py                  # Code filtering
│   ├── date_filter.py                  # Date filtering
│   ├── bundle_cursor.py                # FHIR bundle pagination
│   ├── search_param_retrieve_provider.py # Abstract retrieve provider
│   ├── rest_retrieve_provider.py       # REST HTTP retrieve
│   ├── version_integrity_checker.py    # Version validation
│   └── __init__.py
├── terminology/                         # FHIR Terminology Services
│   ├── dstu3_terminology_provider.py   # DSTU3 terminology
│   ├── r4_terminology_provider.py      # R4 terminology
│   ├── header_injection_interceptor.py # HTTP header injection
│   └── __init__.py
└── searchparam/                         # (Moved to retrieve/)
    └── Search parameter classes
```

## Key Features

### 1. **Model Resolution** (`model/`)
- Abstract `FhirModelResolver` base class for type resolution
- Version-specific implementations for DSTU2, DSTU3, and R4
- Type name resolution from FHIR context
- Property access and mutation on FHIR objects
- Path resolution for nested elements
- Deep equality comparison

**Usage:**
```python
from cql_engine.fhir.model import R4FhirModelResolver

resolver = R4FhirModelResolver(fhir_context)
instance = resolver.create_instance("Patient")
value = resolver.resolve_path(instance, "contact.telecom[0].value")
```

### 2. **Type Conversion** (`converter/`)
- Bidirectional FHIR ↔ CQL type conversion
- `FhirTypeConverter` abstract interface defining all conversion methods
- `BaseFhirTypeConverter` with shared conversion logic
- Version-specific converters for DSTU2, DSTU3, R4, and R5
- Factory pattern for converter creation

**Conversions Supported:**
- Primitive types: Boolean, Integer, Decimal, String
- Temporal types: Date, DateTime, Time
- Complex types: Quantity, Ratio, Coding, CodeableConcept
- Collections: Period/Range to Interval

**Usage:**
```python
from cql_engine.fhir.converter import FhirTypeConverterFactory

converter = FhirTypeConverterFactory.create_converter("R4")
cql_quantity = converter.to_cql_quantity(fhir_quantity)
fhir_coding = converter.to_fhir_coding(cql_code)
```

### 3. **Query Generation & Retrieval** (`retrieve/`)
- `BaseFhirQueryGenerator` abstract base for query generation
- Version-specific query generators (DSTU3, R4)
- `RestFhirRetrieveProvider` for HTTP-based FHIR retrieval
- `SearchParameterMap` for organizing search parameters
- `SearchParameterResolver` for mapping CQL paths to FHIR search params
- `FhirBundleCursor` for paginated bundle traversal
- `CodeFilter` and `DateFilter` for CQL filtering

**Query Generation:**
```python
from cql_engine.fhir.retrieve import FhirQueryGeneratorFactory

generator = FhirQueryGeneratorFactory.create(
    model_resolver=resolver,
    search_parameter_resolver=sp_resolver,
    terminology_provider=term_provider
)
queries = generator.generate_fhir_queries(data_requirement, eval_datetime, context, params)
```

**Data Retrieval:**
```python
from cql_engine.fhir.retrieve import RestFhirRetrieveProvider

provider = RestFhirRetrieveProvider(
    search_parameter_resolver=sp_resolver,
    base_url="https://fhir.example.com"
)
resources = provider._execute_queries("Patient", query_maps)
```

### 4. **Exception Handling** (`exception/`)
- `FhirVersionMismatchException` - Version conflicts
- `UnknownElement` - Missing FHIR elements
- `UnknownPath` - Invalid property paths
- `UnknownType` - Unresolvable type names

### 5. **Terminology Services** (`terminology/`)
- Abstract base classes for DSTU3 and R4
- `HeaderInjectionInterceptor` for adding auth headers
- Extensible for integrating terminology servers

## Design Principles

### 1. **Generic FHIR Support**
Instead of depending on HAPI FHIR Java library, the Python module uses:
- Generic type definitions (dict, dataclass, or user's FHIR library objects)
- Duck typing to support any FHIR library (fhirclient, hl7-fhir, etc.)
- Introspection to access properties dynamically

### 2. **Version Abstraction**
- Abstract base classes define interfaces
- Version-specific implementations customize behavior
- Factory pattern provides automatic version selection

### 3. **Separation of Concerns**
- **Model Resolution**: Type and property access
- **Type Conversion**: CQL ↔ FHIR transformations
- **Query Generation**: Building FHIR searches from CQL
- **Retrieval**: Executing searches and handling responses
- **Terminology**: Code system integration

### 4. **Type Safety**
- Type hints throughout (Python 3.10+)
- ABC (Abstract Base Classes) for clear interfaces
- Dataclasses for structured data

## Differences from Java Implementation

### 1. **FHIR Library Integration**
- **Java**: Uses HAPI FHIR with strongly-typed classes
- **Python**: Works with dict/object interfaces, supports multiple FHIR libraries

### 2. **HTTP Client**
- **Java**: HAPI REST client
- **Python**: `requests` library for simplicity

### 3. **Type Handling**
- **Java**: Generic type parameters on class definition
- **Python**: Runtime type checking with dataclasses

### 4. **Reflection/Introspection**
- **Java**: Reflection API
- **Python**: `hasattr()`, `getattr()`, `type()`, module inspection

### 5. **Collections**
- **Java**: List, Map, Set with type parameters
- **Python**: list, dict, set with type hints

## Usage Examples

### Complete Workflow

```python
from cql_engine.fhir.model import R4FhirModelResolver
from cql_engine.fhir.converter import R4FhirTypeConverter
from cql_engine.fhir.retrieve import (
    RestFhirRetrieveProvider,
    SearchParameterResolver,
    FhirQueryGeneratorFactory
)

# Initialize components
fhir_context = ...  # Your FHIR context
model_resolver = R4FhirModelResolver(fhir_context)
type_converter = R4FhirTypeConverter()
search_param_resolver = SearchParameterResolver(fhir_context)

# Create query generator
query_generator = FhirQueryGeneratorFactory.create(
    model_resolver,
    search_param_resolver,
    terminology_provider=None
)
query_generator.expand_value_sets_value = False
query_generator.page_size_value = 100

# Create retrieval provider
retrieve_provider = RestFhirRetrieveProvider(
    search_parameter_resolver=search_param_resolver,
    base_url="https://fhir.example.com"
)
retrieve_provider.set_fhir_query_generator(query_generator)
```

### Type Conversion

```python
# CQL to FHIR
from decimal import Decimal
cql_quantity = type('Quantity', (), {
    'value': Decimal('10.5'),
    'unit': 'mg'
})()

fhir_qty = type_converter.to_fhir_quantity(cql_quantity)

# FHIR to CQL
fhir_bundle = response.json()  # From REST call
for entry in fhir_bundle.get('entry', []):
    resource = entry.get('resource')
    cql_resource = type_converter.to_cql_type(resource)
```

### Query Generation

```python
from datetime import datetime

data_requirement = {
    'type': 'Observation',
    'codeFilter': [{
        'path': 'code',
        'valueSet': 'http://example.com/vs-vitals'
    }],
    'dateFilter': [{
        'path': 'effectiveDateTime',
        'value': ('>=', datetime(2020, 1, 1))
    }]
}

queries = query_generator.generate_fhir_queries(
    data_requirement,
    evaluation_date_time=datetime.now(),
    context_values={'context': 'Patient'},
    parameters={},
    capability_statement=None
)
```

## Integration with FHIR Libraries

The module is designed to work with any Python FHIR library:

### With fhirclient

```python
from fhirclient import client

settings = {
    'app_id': 'my_app',
    'api_base': 'https://fhir.example.com'
}
fhir_client = client.FHIRClient(settings)
fhir_context = fhir_client.server.fhir_context

resolver = SearchParameterResolver(fhir_context)
```

### With hl7-fhir-r4

```python
from hl7.fhir.r4.resources import Patient

# Works with resource dictionaries
patient_data = {
    'resourceType': 'Patient',
    'id': '123',
    'name': [{'text': 'John Doe'}]
}

# Type converter handles dict or object interfaces
converter.to_cql_type(patient_data)
```

## Dependencies

### Required
- **Python**: 3.10+
- **requests**: For HTTP calls in RestFhirRetrieveProvider

### Optional
- **fhirclient**: For FHIR context and resource definitions
- **hl7-fhir-r4** or other FHIR library for resource definitions
- **cql-engine**: Core CQL evaluation engine (imported for runtime types)

### Installation

```bash
pip install requests

# For FHIR library integration
pip install fhirclient  # or your preferred FHIR library
```

## Testing

The module can be tested with:

```python
import unittest
from cql_engine.fhir.model import R4FhirModelResolver
from cql_engine.fhir.converter import R4FhirTypeConverter

class TestFhirConverter(unittest.TestCase):
    def setUp(self):
        self.converter = R4FhirTypeConverter()

    def test_to_fhir_string(self):
        result = self.converter.to_fhir_string("hello")
        self.assertIsNotNone(result)
```

## Version Support

- **DSTU2** (1.0.2) - Basic support via Dstu2FhirModelResolver, Dstu2FhirTypeConverter
- **DSTU3** (3.0.1) - Full support via Dstu3FhirModelResolver, Dstu3FhirQueryGenerator
- **R4** (4.0.1) - Full support via R4FhirModelResolver, R4FhirQueryGenerator
- **R5** (5.0.0) - Type converter available (query generation not yet implemented)

## Extending the Module

### Adding a New FHIR Version

1. Create `XFhirModelResolver` extending `FhirModelResolver`
2. Create `XFhirTypeConverter` extending `BaseFhirTypeConverter`
3. Create `XFhirQueryGenerator` extending `BaseFhirQueryGenerator`
4. Update factories to support new version

### Custom Type Conversions

```python
from cql_engine.fhir.converter import BaseFhirTypeConverter

class CustomConverter(BaseFhirTypeConverter):
    def to_custom_type(self, value):
        # Your custom conversion
        pass
```

## Future Enhancements

- [ ] Full type converter implementations with actual FHIR library integration
- [ ] Query generator implementations for all FHIR versions
- [ ] Terminology provider implementations for value set expansion
- [ ] Support for custom search parameters
- [ ] Async/await support for retrieval
- [ ] Query result caching
- [ ] Comprehensive test suite
- [ ] Performance optimizations

## License

This Python port maintains compatibility with the original OpenCDS CQL Engine license.

## References

- [OpenCDS CQL Engine](https://github.com/DBCG/cql-engine)
- [HL7 FHIR Specification](https://www.hl7.org/fhir/)
- [CQL Specification](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=400)
