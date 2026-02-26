"""
CQL Engine - Python implementation of the OpenCDS CQL evaluation engine.

A comprehensive Python port of the Java CQL execution engine, providing full support for
evaluating CQL (Clinical Quality Language) expressions and libraries with modern Python idioms.

This package provides:
- Core CQL engine for expression evaluation
- Multiple data providers and model resolvers
- Terminology service integration
- Library loading and caching
- Full execution context management
"""

__version__ = "1.0.0"
__author__ = "OpenCDS"
__license__ = "Apache 2.0"

# Core execution
from cql_engine.execution import (
    CqlEngine,
    CqlEngineOptions,
    Context,
    EvaluationResult,
    ExpressionResult,
    LibraryLoader,
    DefaultLibraryLoader,
    InMemoryLibraryLoader,
    Variable,
    NamespaceHelper,
)

# Data providers
from cql_engine.data import (
    DataProvider,
    CompositeDataProvider,
    SystemDataProvider,
    ExternalFunctionProvider,
    SystemExternalFunctionProvider,
)

# Model resolution
from cql_engine.model import (
    ModelResolver,
    BaseModelResolver,
)

# Retrieval
from cql_engine.retrieve import (
    RetrieveProvider,
    TerminologyAwareRetrieveProvider,
)

# Terminology
from cql_engine.terminology import (
    TerminologyProvider,
    CodeSystemInfo,
    ValueSetInfo,
    TerminologyValidation,
)

# Serialization
from cql_engine.serializing import (
    CqlLibraryReader,
    CqlLibraryReaderProvider,
    CqlLibraryReaderFactory,
    LibraryWrapper,
)

__all__ = [
    # Execution
    'CqlEngine',
    'CqlEngineOptions',
    'Context',
    'EvaluationResult',
    'ExpressionResult',
    'LibraryLoader',
    'DefaultLibraryLoader',
    'InMemoryLibraryLoader',
    'Variable',
    'NamespaceHelper',
    # Data
    'DataProvider',
    'CompositeDataProvider',
    'SystemDataProvider',
    'ExternalFunctionProvider',
    'SystemExternalFunctionProvider',
    # Model
    'ModelResolver',
    'BaseModelResolver',
    # Retrieve
    'RetrieveProvider',
    'TerminologyAwareRetrieveProvider',
    # Terminology
    'TerminologyProvider',
    'CodeSystemInfo',
    'ValueSetInfo',
    'TerminologyValidation',
    # Serializing
    'CqlLibraryReader',
    'CqlLibraryReaderProvider',
    'CqlLibraryReaderFactory',
    'LibraryWrapper',
]
