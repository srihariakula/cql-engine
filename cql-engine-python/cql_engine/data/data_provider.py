"""
Data provider interfaces for CQL engine.

Provides abstractions for accessing data and models during CQL evaluation.
"""

from abc import ABC, abstractmethod
from typing import Callable, Iterable, List, Optional
from cql_engine.model.model_resolver import ModelResolver
from cql_engine.retrieve.retrieve_provider import RetrieveProvider
from cql_engine.runtime.code import Code
from cql_engine.runtime.interval import Interval


class PHIObfuscator(ABC):
    """Abstract base for PHI obfuscation."""
    pass


class NoOpPHIObfuscator(PHIObfuscator):
    """No-op PHI obfuscator that performs no obfuscation."""
    pass


class DataProvider(ModelResolver, RetrieveProvider, ABC):
    """
    Provides support for accessing data and models during CQL evaluation.

    Combines ModelResolver and RetrieveProvider interfaces to handle both
    model resolution and data retrieval operations.
    """

    def phi_obfuscation_supplier(self) -> Callable[[], PHIObfuscator]:
        """
        Returns a supplier function for PHI obfuscation.

        By default, returns a supplier that creates NoOpPHIObfuscator instances.
        Can be overridden to provide custom PHI obfuscation strategies.

        Returns:
            Callable that returns a PHIObfuscator instance
        """
        return NoOpPHIObfuscator
