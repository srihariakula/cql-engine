"""CQL Engine FHIR Module.

Provides FHIR-specific implementations for the CQL Engine, including:
- Model resolution for different FHIR versions
- Type conversion between CQL and FHIR
- Query generation and retrieval from FHIR servers
- Terminology support

Example:
    >>> from cql_engine.fhir.retrieve import RestFhirRetrieveProvider
    >>> from cql_engine.fhir.model import R4FhirModelResolver
    >>> from cql_engine.fhir.converter import R4FhirTypeConverter
    >>>
    >>> # Initialize with FHIR server
    >>> retrieve_provider = RestFhirRetrieveProvider(
    ...     search_parameter_resolver=spr,
    ...     base_url="https://fhir.example.com"
    ... )
"""

# Exception classes
from .exception import (
    FhirVersionMismatchException,
    UnknownElement,
    UnknownPath,
    UnknownType,
)

# Model resolvers
from .model import (
    Dstu2FhirModelResolver,
    Dstu3FhirModelResolver,
    FhirModelResolver,
    R4FhirModelResolver,
)

# Type converters
from .converter import (
    BaseFhirTypeConverter,
    Dstu2FhirTypeConverter,
    Dstu3FhirTypeConverter,
    FhirTypeConverter,
    FhirTypeConverterFactory,
    R4FhirTypeConverter,
    R5FhirTypeConverter,
)

# Retrieve providers and generators
from .retrieve import (
    BaseFhirQueryGenerator,
    CodeFilter,
    DateFilter,
    Dstu3FhirQueryGenerator,
    EverythingModeEnum,
    FhirBundleCursor,
    FhirBundleIterator,
    FhirQueryGeneratorFactory,
    FhirVersionEnum,
    FhirVersionIntegrityChecker,
    R4FhirQueryGenerator,
    RestFhirRetrieveProvider,
    RestSearchParameterTypeEnum,
    SearchParamFhirRetrieveProvider,
    SearchParameterMap,
    SearchParameterResolver,
)

# Terminology providers
from .terminology import (
    Dstu3FhirTerminologyProvider,
    HeaderInjectionInterceptor,
    R4FhirTerminologyProvider,
)

__all__ = [
    # Exceptions
    "FhirVersionMismatchException",
    "UnknownElement",
    "UnknownPath",
    "UnknownType",
    # Model resolvers
    "FhirModelResolver",
    "Dstu2FhirModelResolver",
    "Dstu3FhirModelResolver",
    "R4FhirModelResolver",
    # Type converters
    "FhirTypeConverter",
    "BaseFhirTypeConverter",
    "Dstu2FhirTypeConverter",
    "Dstu3FhirTypeConverter",
    "R4FhirTypeConverter",
    "R5FhirTypeConverter",
    "FhirTypeConverterFactory",
    # Retrieve providers and generators
    "BaseFhirQueryGenerator",
    "Dstu3FhirQueryGenerator",
    "R4FhirQueryGenerator",
    "FhirQueryGeneratorFactory",
    "RestFhirRetrieveProvider",
    "SearchParamFhirRetrieveProvider",
    "FhirBundleCursor",
    "FhirBundleIterator",
    # Search parameters
    "SearchParameterResolver",
    "SearchParameterMap",
    "RestSearchParameterTypeEnum",
    "CodeFilter",
    "DateFilter",
    # Version management
    "FhirVersionEnum",
    "FhirVersionIntegrityChecker",
    "EverythingModeEnum",
    # Terminology
    "Dstu3FhirTerminologyProvider",
    "R4FhirTerminologyProvider",
    "HeaderInjectionInterceptor",
]

__version__ = "1.0.0"
__author__ = "OpenCDS"
__description__ = "FHIR module for CQL Engine"
