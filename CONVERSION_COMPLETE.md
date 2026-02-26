# CQL Engine Exception and Debug Modules - Java to Python Conversion

## Summary

Successfully converted the CQL engine exception and debug modules from Java to modern Python. All files have been created with full logic implementation, modern Python patterns (dataclasses, type hints, enums), and proper documentation.

## Exception Module

### Location
`/sessions/beautiful-charming-noether/mnt/claudecode/cql-engine-python/cql_engine/exception/`

### Files Created (19 total)

#### Core Exception Classes

1. **severity.py** - `Severity` enum
   - MESSAGE, WARNING, TRACE, ERROR values
   - String representation methods

2. **cql_exception.py** - `CqlException` base class
   - Flexible initialization supporting multiple argument patterns
   - Source location tracking
   - Severity level support
   - Proper exception chaining with `__cause__`

3. **cql_exception_handler.py** - `CqlExceptionHandler`
   - Thread uncaught exception handler
   - Root cause extraction
   - Stack trace formatting and logging

#### Provider Exceptions

4. **data_provider_exception.py** - `DataProviderException`
   - Extends CqlException
   - Used by DataProvider implementations

5. **terminology_provider_exception.py** - `TerminologyProviderException`
   - Extends CqlException
   - Used by TerminologyProvider implementations

#### Type and Validation Exceptions

6. **invalid_cast.py** - `InvalidCast`
   - Invalid type cast operations

7. **invalid_comparison.py** - `InvalidComparison`
   - Invalid comparison operations

8. **invalid_conversion.py** - `InvalidConversion`
   - Type conversion errors
   - Two-argument form: `InvalidConversion(from_value, to_value)`
   - Single-argument form: `InvalidConversion(message)`

9. **invalid_date.py** - `InvalidDate`
   - Invalid date values

10. **invalid_date_time.py** - `InvalidDateTime`
    - Invalid datetime values
    - Supports cause parameter

11. **invalid_time.py** - `InvalidTime`
    - Invalid time values

12. **invalid_interval.py** - `InvalidInterval`
    - Invalid interval values

13. **invalid_literal.py** - `InvalidLiteral`
    - Invalid literal values

14. **invalid_operator_argument.py** - `InvalidOperatorArgument`
    - Operator argument validation errors
    - Two-argument form: `InvalidOperatorArgument(expected, found)`
    - Single-argument form: `InvalidOperatorArgument(message)`

15. **invalid_precision.py** - `InvalidPrecision`
    - Invalid precision values

16. **type_overflow.py** - `TypeOverflow`
    - Numeric value overflow

17. **type_underflow.py** - `TypeUnderflow`
    - Numeric value underflow

18. **undefined_result.py** - `UndefinedResult`
    - Operations resulting in undefined values

19. **__init__.py** - Module initialization
    - Exports all exception classes
    - Proper `__all__` declaration

## Debug Module

### Location
`/sessions/beautiful-charming-noether/mnt/claudecode/cql-engine-python/cql_engine/debug/`

### Files Created (12 total)

#### Core Debug Classes

1. **location.py** - `Location` class
   - Frozen dataclass for immutability
   - Start/end line and character positions
   - `includes()` method for location range checking
   - `to_locator()` and `from_locator()` string conversion
   - Proper `__hash__()` and `__eq__()` implementations

2. **source_locator.py** - `SourceLocator` class
   - Dataclass structure
   - Library system ID, name, version tracking
   - Node ID and type information
   - Source location reference
   - `strip_evaluator()` static method
   - String representation methods

#### Debug Action and Entry Classes

3. **debug_action.py** - `DebugAction` enum
   - NONE, LOG, TRACE, WATCH values
   - String representation

4. **debug_result_entry.py** - `DebugResultEntry` dataclass
   - Stores single debug result values
   - Getter method

5. **debug_map_entry.py** - `DebugMapEntry` dataclass
   - Maps debug locator to debug action
   - Validation in `__post_init__`

#### Debug Locator Classes

6. **debug_locator.py** - `DebugLocator` class
   - `DebugLocatorType` enum: NODE_ID, NODE_TYPE, LOCATION, EXCEPTION_TYPE
   - Factory methods: `from_location()`, `from_node_id()`, `from_node_type()`, `from_exception_type()`
   - Automatic "Evaluator" suffix handling for NODE_TYPE
   - Proper equality and hashing
   - String representation

#### Library-Level Debug Classes

7. **debug_library_result_entry.py** - `DebugLibraryResultEntry`
   - Dataclass with library name and results dictionary
   - `log_debug_result_entry()` method
   - Automatic locator creation from Element nodes
   - Fallback to node type for non-Element nodes

8. **debug_library_map_entry.py** - `DebugLibraryMapEntry`
   - Manages debug settings for single library
   - Separate storage for node ID and location entries
   - `should_debug()` method with location inclusion checking
   - `add_entry()` and `remove_entry()` methods

#### Global Debug Classes

9. **debug_map.py** - `DebugMap` dataclass
   - Manages debug settings across multiple libraries
   - Library-specific, node-type, and exception-type entries
   - Logging and coverage tracking flags
   - `should_debug_node()` and `should_debug_exception()` methods
   - Add/remove methods for all entry types
   - Enable/disable flags for logging and coverage

10. **debug_result.py** - `DebugResult` dataclass
    - Aggregates debug results from all libraries
    - Collects error messages
    - `log_debug_result()` with error handling
    - `log_debug_error()` for exception tracking
    - Result retrieval methods

#### Utilities

11. **debug_utilities.py** - `DebugUtilities` class
    - Static utility functions
    - `log_debug_result()` using Python logging
    - `to_debug_location()` for node location strings
    - `to_debug_string()` for value representation
    - Special handling for iterables and null values
    - CqlType detection via dynamic import

12. **__init__.py** - Module initialization
    - Exports all debug classes
    - Proper `__all__` declaration

## Key Design Decisions

### 1. Modern Python Features
- **Dataclasses**: Used for simple data holders (Location, SourceLocator, DebugMapEntry, etc.)
- **Type Hints**: Full type annotations on all methods and variables
- **Enums**: Proper use of Python's Enum for Severity, DebugAction, and DebugLocatorType
- **Frozen Dataclasses**: Location uses frozen=True for immutability

### 2. Exception Handling
- Proper use of Python's exception chaining with `__cause__`
- Flexible constructor patterns supporting multiple calling styles
- Integration with Python's logging module

### 3. Circular Import Prevention
- Used `TYPE_CHECKING` with conditional imports for cross-module references
- Lazy imports in methods where needed (e.g., Element, CqlType)

### 4. Method Naming
- Snake_case for methods and variables (Python convention)
- Kept getter/setter pattern where needed for compatibility with Java API
- Additional convenience methods (factory methods, etc.)

### 5. Collections
- Python dict and list instead of Java HashMap and ArrayList
- Field initialization using `field(default_factory=dict)` in dataclasses

## Testing Verification

All files have been validated:
- Python syntax compilation successful
- No import errors
- Proper module initialization with `__all__` exports

## Usage Examples

### Exception Module
```python
from cql_engine.exception import CqlException, InvalidConversion, Severity

# Simple exception
raise CqlException("Something went wrong")

# With severity and source location
raise CqlException(
    "Invalid operation",
    severity=Severity.ERROR,
    source_locator=locator
)

# Type conversion error
raise InvalidConversion(source_value, target_value)
```

### Debug Module
```python
from cql_engine.debug import (
    DebugMap, DebugAction, DebugLocator, Location, DebugResult
)

# Create a debug map
debug_map = DebugMap()

# Add a node ID breakpoint
debug_map.add_debug_entry("MyLibrary",
    DebugLocator.from_node_id("node-123"),
    DebugAction.LOG
)

# Add a location breakpoint
location = Location(1, 10, 2, 20)
debug_map.add_debug_entry("MyLibrary",
    DebugLocator.from_location(location),
    DebugAction.TRACE
)

# Check if should debug
if debug_map.should_debug_node(node, library) == DebugAction.LOG:
    # Log debug info
    pass
```

## File Counts

- **Exception Module**: 19 Python files (18 implementation + 1 __init__)
- **Debug Module**: 12 Python files (11 implementation + 1 __init__)
- **Total**: 31 files created

## Lines of Code (Approximate)

- Exception Module: ~1,200 lines
- Debug Module: ~1,400 lines
- Total: ~2,600 lines of production Python code

All code includes comprehensive docstrings, type hints, and follows PEP 8 conventions.
