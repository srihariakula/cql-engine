"""
CQL Engine data module.

Provides abstractions for data access and external functions during CQL evaluation.
"""

from cql_engine.data.data_provider import DataProvider, PHIObfuscator, NoOpPHIObfuscator
from cql_engine.data.composite_data_provider import CompositeDataProvider
from cql_engine.data.system_data_provider import SystemDataProvider
from cql_engine.data.external_function_provider import ExternalFunctionProvider
from cql_engine.data.system_external_function_provider import SystemExternalFunctionProvider

__all__ = [
    'DataProvider',
    'PHIObfuscator',
    'NoOpPHIObfuscator',
    'CompositeDataProvider',
    'SystemDataProvider',
    'ExternalFunctionProvider',
    'SystemExternalFunctionProvider',
]
