"""Search parameter-based FHIR retrieve provider."""

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional

from .search_parameter_map import SearchParameterMap
from .search_parameter_resolver import SearchParameterResolver
from .query_generator_factory import FhirQueryGeneratorFactory
from .base_query_generator import BaseFhirQueryGenerator


class SearchParamFhirRetrieveProvider(ABC):
    """Abstract base class for search parameter-based FHIR retrieval.

    Handles retrieval of FHIR resources using search parameters derived from CQL
    queries.
    """

    def __init__(
        self,
        search_parameter_resolver: SearchParameterResolver,
        model_resolver: Optional[Any] = None,
    ) -> None:
        """Initialize the retrieve provider.

        Args:
            search_parameter_resolver: Search parameter resolver
            model_resolver: Optional model resolver
        """
        self.search_parameter_resolver = search_parameter_resolver
        self.fhir_context = search_parameter_resolver.get_fhir_context()
        self.model_resolver = model_resolver

        self.page_size: Optional[int] = None
        self.max_codes_per_query: Optional[int] = None
        self.query_batch_threshold: Optional[int] = None
        self.fhir_query_generator: Optional[BaseFhirQueryGenerator] = None

    def set_page_size(self, value: Optional[int]) -> None:
        """Set the page size for paginated retrieval.

        Args:
            value: Page size (must be > 0)

        Raises:
            ValueError: If value is invalid
        """
        if value is not None and value < 1:
            raise ValueError("value must be a non-null integer > 0")
        self.page_size = value

    def get_page_size(self) -> Optional[int]:
        """Get the page size.

        Returns:
            Page size
        """
        return self.page_size

    def set_fhir_query_generator(
        self, fhir_query_generator: BaseFhirQueryGenerator
    ) -> None:
        """Set the FHIR query generator.

        Args:
            fhir_query_generator: Query generator to use
        """
        self.fhir_query_generator = fhir_query_generator

    def get_fhir_query_generator(self) -> Optional[BaseFhirQueryGenerator]:
        """Get the FHIR query generator.

        Returns:
            Query generator, or None if not set
        """
        return self.fhir_query_generator

    def set_model_resolver(self, model_resolver: Optional[Any]) -> None:
        """Set the model resolver.

        Args:
            model_resolver: Model resolver
        """
        self.model_resolver = model_resolver

    def get_model_resolver(self) -> Optional[Any]:
        """Get the model resolver.

        Returns:
            Model resolver
        """
        return self.model_resolver

    def set_max_codes_per_query(self, value: Optional[int]) -> None:
        """Set the maximum codes per query.

        Args:
            value: Max codes (must be > 0)

        Raises:
            ValueError: If value is invalid
        """
        if value is not None and value < 1:
            raise ValueError("value must be a non-null integer > 0")
        self.max_codes_per_query = value

    def get_max_codes_per_query(self) -> Optional[int]:
        """Get the maximum codes per query.

        Returns:
            Max codes per query
        """
        return self.max_codes_per_query

    def set_query_batch_threshold(self, value: Optional[int]) -> None:
        """Set the query batch threshold.

        Args:
            value: Batch threshold (must be > 0)

        Raises:
            ValueError: If value is invalid
        """
        if value is not None and value < 1:
            raise ValueError("value must be a non-null integer > 0")
        self.query_batch_threshold = value

    def get_query_batch_threshold(self) -> Optional[int]:
        """Get the query batch threshold.

        Returns:
            Batch threshold
        """
        return self.query_batch_threshold

    def _ensure_query_generator(self) -> BaseFhirQueryGenerator:
        """Ensure a query generator is available.

        Returns:
            Query generator

        Raises:
            ValueError: If generator cannot be created
        """
        if not self.fhir_query_generator:
            self.fhir_query_generator = FhirQueryGeneratorFactory.create_with_options(
                self.model_resolver,
                self.search_parameter_resolver,
                None,  # terminology_provider
                None,  # should_expand_value_sets
                self.max_codes_per_query,
                self.page_size,
                self.query_batch_threshold,
            )

        return self.fhir_query_generator

    @abstractmethod
    def _execute_queries(
        self, data_type: str, queries: List[SearchParameterMap]
    ) -> Iterable[Any]:
        """Execute the queries.

        Args:
            data_type: FHIR resource type
            queries: List of search parameter maps

        Returns:
            Iterable of retrieved resources
        """
        pass

    def retrieve(self, context: str, context_value: Optional[str]) -> Iterable[Any]:
        """Retrieve resources for a context.

        Args:
            context: Context type (e.g., 'Patient')
            context_value: Context value (e.g., patient ID)

        Returns:
            Iterable of resources
        """
        return []
