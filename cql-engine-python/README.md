# CQL Engine Python Implementation

Modern Python 3.10+ implementation of the OpenCDS CQL (Clinical Quality Language) execution engine core modules.

## Overview

This is a faithful port of the critical Java CQL Engine modules to Python, maintaining full compatibility with the original architecture while leveraging modern Python idioms and best practices.

## Modules

### Core Execution (`cql_engine.execution`)
- **CqlEngine**: Main execution engine for evaluating CQL libraries
- **Context**: Thread-affine execution context managing all evaluation state
- **Variable**: Variable tracking in execution context
- **NamespaceHelper**: URI and name parsing utilities
- **LibraryLoader**: Interface for library discovery and loading
- **DefaultLibraryLoader**: Placeholder loader implementation
- **InMemoryLibraryLoader**: In-memory library cache
- **EvaluationResult**: Container for expression evaluation results
- **ExpressionResult**: Individual expression result with evaluated resources

### Data Access (`cql_engine.data`)
- **DataProvider**: Combined interface for model resolution and data retrieval
- **CompositeDataProvider**: Delegates to separate model and retrieve providers
- **SystemDataProvider**: Built-in provider for CQL system types
- **ExternalFunctionProvider**: Interface for external function evaluation
- **SystemExternalFunctionProvider**: Default external function provider
- **PHIObfuscator**: PHI obfuscation abstraction

### Model Resolution (`cql_engine.model`)
- **ModelResolver**: Abstract interface for mapping logical to physical models
- **BaseModelResolver**: Base implementation with type casting

### Data Retrieval (`cql_engine.retrieve`)
- **RetrieveProvider**: Abstract data retrieval interface
- **TerminologyAwareRetrieveProvider**: Retrieval with terminology support

### Terminology Services (`cql_engine.terminology`)
- **TerminologyProvider**: Code system and value set operations
- **CodeSystemInfo**: Code system metadata
- **ValueSetInfo**: Value set metadata with code systems
- **TerminologyValidation**: Standard medical coding system registry

### Library Serialization (`cql_engine.serializing`)
- **CqlLibraryReader**: Abstract library reader interface
- **CqlLibraryReaderProvider**: Service provider for readers
- **CqlLibraryReaderFactory**: Factory for obtaining readers
- **LibraryWrapper**: Simple library container

## Quick Start

```python
from cql_engine.execution import CqlEngine, InMemoryLibraryLoader, CqlEngineOptions
from cql_engine.data import SystemDataProvider, CompositeDataProvider
from cql_engine.terminology import TerminologyProvider

# Create a library loader
loader = InMemoryLibraryLoader([library1, library2])

# Create data providers
data_providers = {
    "urn:hl7-org:elm-types:r1": SystemDataProvider(),
    "http://hl7.org/fhir": FhirDataProvider(),  # Your implementation
}

# Create terminology provider
terminology_provider = MyTerminologyProvider()  # Your implementation

# Create engine with options
engine = CqlEngine(
    library_loader=loader,
    data_providers=data_providers,
    terminology_provider=terminology_provider,
    engine_options={
        CqlEngineOptions.ENABLE_EXPRESSION_CACHING,
        CqlEngineOptions.ENABLE_VALIDATION
    }
)

# Evaluate a library
from datetime import datetime, timezone
result = engine.evaluate_versioned(
    library_identifier=library_id,
    expressions={'expression1', 'expression2'},
    parameters={'param1': value1},
    evaluation_datetime=datetime.now(timezone.utc)
)

# Access results
for expr_name, expr_result in result.expression_results.items():
    print(f"{expr_name}: {expr_result.value()}")
```

## Architecture

### Execution Flow

1. **Engine Creation**: Initialize `CqlEngine` with loaders and providers
2. **Library Loading**: Use `LibraryLoader` to load and cache libraries
3. **Context Initialization**: Create `Context` with evaluation state
4. **Parameter Setting**: Set expression parameters and context values
5. **Expression Evaluation**: Evaluate selected expressions
6. **Result Aggregation**: Collect results in `EvaluationResult`

### Key Patterns

#### Builder Pattern
Many classes support fluent configuration:
```python
CodeSystemInfo().with_id("http://snomed.info/sct").with_version("2023-01-01")
```

#### Provider Pattern
Pluggable implementations for:
- Data access (DataProvider)
- Data retrieval (RetrieveProvider)
- Terminology services (TerminologyProvider)
- External functions (ExternalFunctionProvider)
- Library loading (LibraryLoader)

#### Factory Pattern
Service provider interface for library readers with content-type selection:
```python
reader = CqlLibraryReaderFactory.get_reader("application/json")
library = reader.read_file("path/to/library.json")
```

## Type System

Full Python 3.10+ type hints throughout:

```python
def register_data_provider(
    self,
    model_uri: str,
    data_provider: DataProvider
) -> None:
    """Register a data provider for a model."""
```

## Error Handling

Custom exceptions for specific error conditions:
- `CqlException`: General CQL execution error
- `InvalidCast`: Type casting failure
- `ValueError`: Invalid argument or state

## Performance Features

- Expression result caching with LRU behavior
- Lazy library loading
- In-memory library caching
- Efficient variable stack management

## Thread Safety

The `Context` class maintains evaluation state. While individual contexts are not thread-safe, they are designed to be thread-affine - one context per evaluation thread.

## Modern Python Features

- Full type hints (PEP 484)
- Abstract base classes for interfaces
- Enums for options
- Builder pattern with fluent API
- Context managers ready
- Comprehensive docstrings

## Dependencies

Only standard library dependencies:
- `typing`: Type hints
- `abc`: Abstract base classes
- `enum`: Enumerations
- `collections`: OrderedDict for LRU
- `datetime`: DateTime handling

## Integration Notes

### External Dependencies
The modules reference external types that need implementation:
- `Library`: ELM Library type
- `Code`, `Interval`, `DateTime`: Runtime types
- `ValueSet`, `CodeSystem`: Terminology types
- `ExpressionDef`, `FunctionDef`: ELM definitions

Replace stub imports with actual implementations from:
- `cql-elm-execution` (ELM execution objects)
- `cql-elm-fhir` (FHIR model support)

### Custom Implementations

Implement these interfaces for your use case:
- `DataProvider`: Custom model resolution
- `RetrieveProvider`: Custom data retrieval
- `TerminologyProvider`: Terminology service integration
- `LibraryLoader`: Custom library discovery
- `ExternalFunctionProvider`: Custom function execution

## Testing

Each module includes:
- Comprehensive docstrings with examples
- Type hints for IDE support
- Clear error messages
- Validation of inputs

Write tests for:
- Custom provider implementations
- Library loading and caching
- Expression evaluation
- Parameter and context management
- Multi-library scenarios

## Conversion Notes

This is a direct port from the Java OpenCDS CQL engine. Key conversion decisions:

1. **Interfaces → ABCs**: Java interfaces become Python ABC classes
2. **Naming**: Java camelCase → Python snake_case for methods
3. **Null → None**: Java null → Python None
4. **Collections**: Java Map/List → Python dict/list with typing
5. **Reflection**: Java getMethod/getDeclaredField → Python getattr/hasattr
6. **Generics**: Java generic types → Python type hints
7. **Enums**: Java EnumSet → Python set of Enum values

## Future Enhancements

- Async library loading support
- Thread pool integration
- Expression pre-compilation
- Query optimization
- Performance profiling
- More comprehensive caching

## License

Apache License 2.0 - See LICENSE file

## Original Source

Converted from the OpenCDS CQL Engine:
- Repository: https://github.com/cqframework/cql-engine
- Language: Java
- Version: Latest
