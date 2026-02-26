# CQL Engine Exception and Debug Modules - Quick Reference

## Exception Module Classes

### Base Exception
- **CqlException**: Base exception with severity and source location support
  ```python
  CqlException(message, cause=None, source_locator=None, severity=Severity.ERROR)
  ```

### Severity Enum
- **Severity.MESSAGE**, **Severity.WARNING**, **Severity.TRACE**, **Severity.ERROR**

### Provider Exceptions
- **DataProviderException**: Thrown by DataProvider implementations
- **TerminologyProviderException**: Thrown by TerminologyProvider implementations

### Type/Value Exceptions
- **InvalidCast**: Invalid type cast
- **InvalidComparison**: Invalid comparison operation
- **InvalidConversion**: Type conversion error
  - `InvalidConversion(message)` or `InvalidConversion(from_type, to_type)`
- **InvalidDate**: Invalid date value
- **InvalidDateTime**: Invalid datetime value
- **InvalidTime**: Invalid time value
- **InvalidInterval**: Invalid interval value
- **InvalidLiteral**: Invalid literal value
- **InvalidOperatorArgument**: Operator argument error
  - `InvalidOperatorArgument(message)` or `InvalidOperatorArgument(expected, found)`
- **InvalidPrecision**: Invalid precision value
- **TypeOverflow**: Numeric overflow
- **TypeUnderflow**: Numeric underflow
- **UndefinedResult**: Operation resulted in undefined value

### Utilities
- **CqlExceptionHandler**: Uncaught exception handler for threads

## Debug Module Classes

### Location
- **Location**: Identifies position in source file
  - `Location(start_line, start_char, end_line, end_char)`
  - `includes(other)`: Check if location includes another
  - `to_locator()`: Convert to string format
  - `from_locator(locator_string)`: Parse from string

### Source Location
- **SourceLocator**: Locates a node in source code
  - Library info, node ID/type, and source location
  - `strip_evaluator(node_type)`: Remove "Evaluator" suffix

### Debug Action
- **DebugAction.NONE**: No debugging
- **DebugAction.LOG**: Log the result
- **DebugAction.TRACE**: Trace execution
- **DebugAction.WATCH**: Watch the value

### Debug Locators
- **DebugLocatorType**: Type enum (NODE_ID, NODE_TYPE, LOCATION, EXCEPTION_TYPE)
- **DebugLocator**: Specifies a breakpoint
  - Factory methods: `from_location()`, `from_node_id()`, `from_node_type()`, `from_exception_type()`

### Debug Entries
- **DebugMapEntry**: Maps locator to action
- **DebugResultEntry**: Stores debug result value

### Library Debug Management
- **DebugLibraryMapEntry**: Manages debug settings for single library
  - `should_debug(node)`: Check if node should be debugged
  - `add_entry()`, `remove_entry()`: Manage breakpoints

- **DebugLibraryResultEntry**: Stores debug results for single library
  - `log_debug_result_entry()`: Log a result
  - `get_results()`: Get all results

### Global Debug Management
- **DebugMap**: Manages all debug settings
  - `should_debug_node()`: Check if node should debug
  - `should_debug_exception()`: Check if exception should debug
  - `add_debug_entry()`, `remove_debug_entry()`: Global breakpoint management
  - Logging and coverage flags

- **DebugResult**: Aggregates all debug data
  - `log_debug_result()`: Log execution result
  - `log_debug_error()`: Log exception
  - `get_messages()`, `get_library_results()`: Retrieve data

### Utilities
- **DebugUtilities**: Static utility methods
  - `log_debug_result()`: Use Python logging
  - `to_debug_location()`: Format location string
  - `to_debug_string()`: Format value for display

## Module Imports

### Exception Module
```python
from cql_engine.exception import (
    CqlException,
    CqlExceptionHandler,
    Severity,
    DataProviderException,
    TerminologyProviderException,
    InvalidCast,
    InvalidComparison,
    InvalidConversion,
    InvalidDate,
    InvalidDateTime,
    InvalidTime,
    InvalidInterval,
    InvalidLiteral,
    InvalidOperatorArgument,
    InvalidPrecision,
    TypeOverflow,
    TypeUnderflow,
    UndefinedResult,
)
```

### Debug Module
```python
from cql_engine.debug import (
    DebugAction,
    DebugLocator,
    DebugLocatorType,
    DebugMap,
    DebugResult,
    Location,
    SourceLocator,
    DebugUtilities,
)
```

## Common Patterns

### Creating Exceptions
```python
# Simple message
raise CqlException("An error occurred")

# With cause
try:
    # some operation
except Exception as e:
    raise CqlException("Failed to process", cause=e)

# With severity and location
raise InvalidDate(
    "Date must be valid",
    severity=Severity.WARNING,
    source_locator=locator
)
```

### Setting Up Debugging
```python
debug_map = DebugMap()

# Enable logging
debug_map.set_is_logging_enabled(True)

# Add breakpoint by node ID
debug_map.add_debug_entry(
    "MyLibrary",
    DebugLocator.from_node_id("node-42"),
    DebugAction.LOG
)

# Add breakpoint by location range
location = Location(10, 5, 15, 20)
debug_map.add_debug_entry(
    "MyLibrary",
    DebugLocator.from_location(location),
    DebugAction.TRACE
)
```

### Capturing Debug Results
```python
debug_result = DebugResult()

# During execution
for node, result, library in nodes_to_execute:
    action = debug_map.should_debug_node(node, library)
    if action != DebugAction.NONE:
        debug_result.log_debug_result(node, library, result, action)

# Retrieve results
messages = debug_result.get_messages()
library_results = debug_result.get_library_results()
```

## File Organization

```
cql_engine/
├── exception/
│   ├── __init__.py
│   ├── severity.py
│   ├── cql_exception.py
│   ├── cql_exception_handler.py
│   ├── data_provider_exception.py
│   ├── terminology_provider_exception.py
│   ├── invalid_*.py (13 files)
│   ├── type_overflow.py
│   ├── type_underflow.py
│   └── undefined_result.py
└── debug/
    ├── __init__.py
    ├── location.py
    ├── source_locator.py
    ├── debug_action.py
    ├── debug_locator.py
    ├── debug_result_entry.py
    ├── debug_map_entry.py
    ├── debug_utilities.py
    ├── debug_library_result_entry.py
    ├── debug_library_map_entry.py
    ├── debug_map.py
    └── debug_result.py
```

## Key Differences from Java

1. **Snake_case** for Python naming conventions
2. **Type hints** instead of Java type declarations
3. **Dataclasses** instead of JavaBean pattern
4. **Enums** as Python Enum class
5. **Frozen dataclasses** for immutable objects
6. **Property methods** (get_/set_) for compatibility but Pythonic attribute access also supported
7. **Logging** module instead of log4j
8. **Lazy imports** to avoid circular dependencies

## Python Version Requirements

- Python 3.10+ (for modern union syntax and match statements if used)
- dataclasses (built-in since Python 3.7)
- typing (built-in since Python 3.5)
- enum (built-in since Python 3.4)
- logging (built-in)
