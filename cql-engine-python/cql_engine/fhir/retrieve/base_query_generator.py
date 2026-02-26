"""Base FHIR query generator."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from collections.abc import Iterable as IterableABC

from .search_parameter_map import SearchParameterMap
from .search_parameter_resolver import SearchParameterResolver, RestSearchParameterTypeEnum
from .code_filter import CodeFilter
from .date_filter import DateFilter
from .version_integrity_checker import FhirVersionIntegrityChecker, FhirVersionEnum
from ..exception import FhirVersionMismatchException


class BaseFhirQueryGenerator(FhirVersionIntegrityChecker, ABC):
    """Abstract base for FHIR version-specific query generators.

    Generates FHIR search queries from CQL data requirements and filters.
    """

    DEFAULT_SHOULD_EXPAND_VALUESETS = False

    def __init__(
        self,
        search_parameter_resolver: SearchParameterResolver,
        terminology_provider: Optional[Any],
        model_resolver: Optional[Any],
        fhir_context: Optional[Any],
    ) -> None:
        """Initialize the query generator.

        Args:
            search_parameter_resolver: Resolver for search parameters
            terminology_provider: Provider for terminology services
            model_resolver: Resolver for FHIR model types
            fhir_context: FHIR context

        Raises:
            FhirVersionMismatchException: If FHIR versions don't match
        """
        self.search_parameter_resolver = search_parameter_resolver
        self.terminology_provider = terminology_provider
        self.model_resolver = model_resolver
        self.fhir_context = fhir_context

        self.page_size: Optional[int] = None
        self.max_codes_per_query: Optional[int] = None
        self.query_batch_threshold: Optional[int] = None
        self.expand_value_sets = self.DEFAULT_SHOULD_EXPAND_VALUESETS

        if fhir_context:
            version_enum = self.fetch_fhir_version_enum(fhir_context)
            self.validate_fhir_version_integrity(version_enum)

    def validate_fhir_version_integrity(
        self, fhir_version_enum: FhirVersionEnum
    ) -> None:
        """Validate FHIR version integrity.

        Args:
            fhir_version_enum: FHIR version to validate

        Raises:
            FhirVersionMismatchException: If versions don't match
        """
        if (
            self.search_parameter_resolver
            and self.fetch_fhir_version_enum(
                self.search_parameter_resolver.get_fhir_context()
            )
            != fhir_version_enum
        ):
            raise FhirVersionMismatchException(
                "Components have different FHIR versions"
            )

    @property
    def page_size_value(self) -> Optional[int]:
        """Get page size."""
        return self.page_size

    @page_size_value.setter
    def page_size_value(self, value: Optional[int]) -> None:
        """Set page size.

        Args:
            value: Page size (must be > 0)

        Raises:
            ValueError: If value is invalid
        """
        if value is not None and value < 1:
            raise ValueError("value must be a non-null integer > 0")
        self.page_size = value

    @property
    def max_codes_per_query_value(self) -> Optional[int]:
        """Get max codes per query."""
        return self.max_codes_per_query

    @max_codes_per_query_value.setter
    def max_codes_per_query_value(self, value: Optional[int]) -> None:
        """Set max codes per query.

        Args:
            value: Max codes (must be > 0)

        Raises:
            ValueError: If value is invalid
        """
        if value is not None and value < 1:
            raise ValueError("value must be non-null integer > 0")
        self.max_codes_per_query = value

    @property
    def query_batch_threshold_value(self) -> Optional[int]:
        """Get query batch threshold."""
        return self.query_batch_threshold

    @query_batch_threshold_value.setter
    def query_batch_threshold_value(self, value: Optional[int]) -> None:
        """Set query batch threshold.

        Args:
            value: Batch threshold (must be > 0)

        Raises:
            ValueError: If value is invalid
        """
        if value is not None and value < 1:
            raise ValueError("value must be non-null integer > 0")
        self.query_batch_threshold = value

    @property
    def expand_value_sets_value(self) -> bool:
        """Check if value sets should be expanded."""
        return self.expand_value_sets

    @expand_value_sets_value.setter
    def expand_value_sets_value(self, value: bool) -> None:
        """Set whether to expand value sets.

        Args:
            value: True to expand value sets
        """
        self.expand_value_sets = value

    @abstractmethod
    def generate_fhir_queries(
        self,
        data_requirement: Any,
        evaluation_date_time: Optional[datetime],
        context_values: Optional[Dict[str, Any]],
        parameters: Optional[Dict[str, Any]],
        capability_statement: Optional[Any],
    ) -> List[str]:
        """Generate FHIR queries from a data requirement.

        Args:
            data_requirement: CQL data requirement
            evaluation_date_time: Evaluation date/time
            context_values: Context values
            parameters: CQL parameters
            capability_statement: FHIR CapabilityStatement

        Returns:
            List of generated query strings
        """
        pass

    @abstractmethod
    def get_fhir_version(self) -> FhirVersionEnum:
        """Get the FHIR version this generator handles.

        Returns:
            The FHIR version
        """
        pass

    def _get_template_param(self, data_type: str, template_id: Optional[str]) -> Optional[Tuple[str, Any]]:
        """Get template parameter for query.

        Args:
            data_type: Resource type
            template_id: Template/profile ID

        Returns:
            Tuple of (param_name, param_value), or None
        """
        if not template_id:
            return None
        return None

    def _get_date_range_param(
        self,
        data_type: str,
        date_path: Optional[str],
        date_low_path: Optional[str],
        date_high_path: Optional[str],
        date_range: Optional[Any],
    ) -> Optional[Tuple[str, Any]]:
        """Get date range parameter for query.

        Args:
            data_type: Resource type
            date_path: Path to date element
            date_low_path: Path to low date
            date_high_path: Path to high date
            date_range: Interval for date range

        Returns:
            Tuple of (param_name, date_range_param), or None
        """
        if not date_range:
            return None

        try:
            param_def = self.search_parameter_resolver.get_search_parameter_definition(
                data_type, date_path, RestSearchParameterTypeEnum.DATE
            )
            if not param_def:
                raise ValueError(
                    f"Could not resolve search parameter with date type for {data_type}.{date_path}"
                )

            # Return parameter name and date range
            return (param_def.get_name() if hasattr(param_def, 'get_name') else str(param_def), date_range)
        except Exception:
            pass

        return None

    def _get_context_param(
        self,
        data_type: str,
        context: Optional[str],
        context_path: Optional[str],
        context_value: Optional[Any],
    ) -> Optional[Tuple[str, Any]]:
        """Get context parameter for query.

        Args:
            data_type: Resource type
            context: Context type (e.g., 'Patient')
            context_path: Context path
            context_value: Context value

        Returns:
            Tuple of (param_name, param_value), or None
        """
        if context == "Patient" and context_value and context_path:
            return self.search_parameter_resolver.create_search_parameter(
                context, data_type, context_path, str(context_value)
            )
        return None

    def _get_code_params(
        self,
        data_type: str,
        code_path: Optional[str],
        codes: Optional[IterableABC],
        value_set: Optional[str],
    ) -> Optional[Tuple[str, List[Any]]]:
        """Get code parameters for query.

        Args:
            data_type: Resource type
            code_path: Path to code element
            codes: Iterable of Code objects
            value_set: ValueSet URL

        Returns:
            Tuple of (param_name, code_params), or None
        """
        if not code_path or (not codes and not value_set):
            if code_path is None and (codes or value_set):
                raise ValueError(
                    "A code path must be provided when filtering on codes or a valueset."
                )
            return None

        # Normalize value set URN
        if value_set and value_set.startswith("urn:oid:"):
            value_set = value_set.replace("urn:oid:", "")

        # Get code parameters
        code_param_lists = self._process_code_params(codes, value_set)
        if not code_param_lists:
            return None

        param_def = self.search_parameter_resolver.get_search_parameter_definition(
            data_type, code_path, RestSearchParameterTypeEnum.TOKEN
        )

        if not param_def:
            return None

        param_name = param_def.get_name() if hasattr(param_def, 'get_name') else str(param_def)
        return (param_name, code_param_lists)

    def _process_code_params(
        self, codes: Optional[IterableABC], value_set: Optional[str]
    ) -> List[Any]:
        """Process code parameters.

        Args:
            codes: Iterable of Code objects
            value_set: ValueSet URL

        Returns:
            List of code parameter lists
        """
        if value_set:
            if not self.expand_value_sets:
                # Return ValueSet URL with :in modifier
                return [("valueset", value_set)]

            # Expand value set if terminology provider available
            if self.terminology_provider:
                try:
                    codes = self.terminology_provider.expand({"id": value_set})
                except Exception:
                    codes = []

        if not codes:
            return []

        # Check batch threshold
        codes_list = self._iterable_to_list(codes)
        if self.max_codes_per_query and self.query_batch_threshold:
            num_queries = len(codes_list) / float(self.max_codes_per_query)
            if num_queries > self.query_batch_threshold:
                return []

        # Chunk codes by max_codes_per_query
        code_params = []
        chunk = []

        for idx, code in enumerate(codes_list):
            if self.max_codes_per_query and idx % self.max_codes_per_query == 0:
                if chunk:
                    code_params.append(chunk)
                chunk = []

            # Extract code system and code
            if hasattr(code, "system") and hasattr(code, "code"):
                chunk.append((code.system, code.code))
            elif hasattr(code, "get_system") and hasattr(code, "get_code"):
                chunk.append((code.get_system(), code.get_code()))
            else:
                chunk.append((None, str(code)))

        if chunk:
            code_params.append(chunk)

        return code_params

    def _setup_queries(
        self,
        context: Optional[str],
        context_path: Optional[str],
        context_value: Optional[Any],
        data_type: str,
        template_id: Optional[str],
        code_filters: Optional[List[CodeFilter]],
        date_filters: Optional[List[DateFilter]],
    ) -> List[SearchParameterMap]:
        """Setup search parameter maps from filters.

        Args:
            context: Context type
            context_path: Context path
            context_value: Context value
            data_type: Resource type
            template_id: Template ID
            code_filters: List of code filters
            date_filters: List of date filters

        Returns:
            List of SearchParameterMaps
        """
        template_param = self._get_template_param(data_type, template_id)

        context_param = self._get_context_param(
            data_type, context, context_path, context_value
        )

        date_range_params = []
        if date_filters:
            for df in date_filters:
                date_range_param = self._get_date_range_param(
                    data_type,
                    df.get_date_path(),
                    df.get_date_low_path(),
                    df.get_date_high_path(),
                    df.get_date_range(),
                )
                if date_range_param:
                    date_range_params.append(date_range_param)

        code_param_list = []
        if code_filters:
            for cf in code_filters:
                code_params = self._get_code_params(
                    data_type, cf.get_code_path(), cf.get_codes(), cf.get_value_set()
                )
                if code_params:
                    code_param_list.append(code_params)

        return self._inner_setup_queries(
            template_param, context_param, date_range_params, code_param_list
        )

    def _inner_setup_queries(
        self,
        template_param: Optional[Tuple[str, Any]],
        context_param: Optional[Tuple[str, Any]],
        date_range_params: List[Tuple[str, Any]],
        code_params: List[Tuple[str, List[Any]]],
    ) -> List[SearchParameterMap]:
        """Inner setup queries with chunking support.

        Args:
            template_param: Template parameter
            context_param: Context parameter
            date_range_params: List of date range parameters
            code_params: List of code parameter lists

        Returns:
            List of SearchParameterMaps
        """
        if not code_params:
            return [
                self._get_base_map(
                    template_param, context_param, date_range_params, code_params
                )
            ]

        # Check for chunked code parameters
        chunked_param = None
        for param_name, param_list in code_params:
            if isinstance(param_list, list) and len(param_list) > 1:
                if chunked_param:
                    raise ValueError(
                        f"Cannot evaluate multiple chunked code filters on {chunked_param[0]} and {param_name}"
                    )
                chunked_param = (param_name, param_list)

        if not chunked_param:
            return [
                self._get_base_map(
                    template_param, context_param, date_range_params, code_params
                )
            ]

        # Create separate query for each chunk
        maps = []
        for chunk in chunked_param[1]:
            base = self._get_base_map(
                template_param, context_param, date_range_params, code_params
            )
            base.add(chunked_param[0], chunk)
            maps.append(base)

        return maps

    def _get_base_map(
        self,
        template_param: Optional[Tuple[str, Any]],
        context_param: Optional[Tuple[str, Any]],
        date_range_params: List[Tuple[str, Any]],
        code_params: List[Tuple[str, List[Any]]],
    ) -> SearchParameterMap:
        """Get base search parameter map.

        Args:
            template_param: Template parameter
            context_param: Context parameter
            date_range_params: List of date parameters
            code_params: List of code parameters

        Returns:
            SearchParameterMap
        """
        base_map = SearchParameterMap()

        if self.page_size:
            base_map.count = self.page_size

        if template_param:
            base_map.add(template_param[0], template_param[1])

        for param_name, param_value in date_range_params:
            base_map.add(param_name, param_value)

        for param_name, param_list in code_params:
            # Skip chunked parameters
            if isinstance(param_list, list) and len(param_list) <= 1:
                if param_list:
                    base_map.add(param_name, param_list[0])

        if context_param:
            base_map.add(context_param[0], context_param[1])

        return base_map

    @staticmethod
    def _iterable_to_list(iterable: IterableABC) -> List[Any]:
        """Convert an iterable to a list.

        Args:
            iterable: Iterable object

        Returns:
            List of items
        """
        if isinstance(iterable, list):
            return iterable
        if isinstance(iterable, set):
            return list(iterable)
        return list(iterable)
