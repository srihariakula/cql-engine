"""
Terminology-aware retrieve provider for CQL engine.

Provides data retrieval with support for terminology expansion and validation.
"""

from typing import Optional
from cql_engine.retrieve.retrieve_provider import RetrieveProvider
from cql_engine.terminology.terminology_provider import TerminologyProvider


class TerminologyAwareRetrieveProvider(RetrieveProvider):
    """
    Abstract retrieve provider that is aware of terminology services.

    Extends RetrieveProvider with terminology capabilities including value set expansion
    and code system lookups during data retrieval.
    """

    def __init__(self):
        """Initialize the terminology-aware retrieve provider."""
        self.terminology_provider: Optional[TerminologyProvider] = None
        self.expand_value_sets: bool = False

    def is_expand_value_sets(self) -> bool:
        """
        Check if value sets should be expanded during retrieval.

        Returns:
            True if value sets should be expanded, False otherwise
        """
        return self.expand_value_sets

    def set_expand_value_sets(self, expand_value_sets: bool) -> 'TerminologyAwareRetrieveProvider':
        """
        Set whether value sets should be expanded during retrieval.

        Args:
            expand_value_sets: True to expand value sets, False otherwise

        Returns:
            Self for method chaining
        """
        self.expand_value_sets = expand_value_sets
        return self

    def get_terminology_provider(self) -> Optional[TerminologyProvider]:
        """
        Get the terminology provider.

        Returns:
            The registered TerminologyProvider or None if not registered
        """
        return self.terminology_provider

    def set_terminology_provider(self, terminology_provider: TerminologyProvider) -> None:
        """
        Set the terminology provider.

        Args:
            terminology_provider: The TerminologyProvider to use for terminology operations
        """
        self.terminology_provider = terminology_provider
