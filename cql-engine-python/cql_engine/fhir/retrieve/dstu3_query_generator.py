"""DSTU3-specific FHIR query generator."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_query_generator import BaseFhirQueryGenerator
from .version_integrity_checker import FhirVersionEnum
from .search_parameter_resolver import SearchParameterResolver


class Dstu3FhirQueryGenerator(BaseFhirQueryGenerator):
    """FHIR query generator for DSTU3 (HL7 FHIR version 3.0.0)."""

    def __init__(
        self,
        search_parameter_resolver: SearchParameterResolver,
        terminology_provider: Optional[Any],
        model_resolver: Optional[Any],
    ) -> None:
        """Initialize DSTU3 query generator.

        Args:
            search_parameter_resolver: Search parameter resolver
            terminology_provider: Terminology provider
            model_resolver: Model resolver
        """
        super().__init__(
            search_parameter_resolver,
            terminology_provider,
            model_resolver,
            search_parameter_resolver.get_fhir_context() if search_parameter_resolver else None,
        )

    def get_fhir_version(self) -> FhirVersionEnum:
        """Get FHIR version.

        Returns:
            DSTU3
        """
        return FhirVersionEnum.DSTU3

    def generate_fhir_queries(
        self,
        data_requirement: Any,
        evaluation_date_time: Optional[datetime],
        context_values: Optional[Dict[str, Any]],
        parameters: Optional[Dict[str, Any]],
        capability_statement: Optional[Any],
    ) -> List[str]:
        """Generate FHIR queries for DSTU3.

        Args:
            data_requirement: CQL data requirement
            evaluation_date_time: Evaluation date time
            context_values: Context values
            parameters: Parameters
            capability_statement: Capability statement

        Returns:
            List of query strings
        """
        # Extract data requirement properties
        data_type = getattr(data_requirement, 'type', None)
        if not data_type:
            return []

        code_filters = self._extract_code_filters(data_requirement)
        date_filters = self._extract_date_filters(data_requirement)

        # Setup queries
        context = context_values.get('context') if context_values else None
        context_value = context_values.get('contextValue') if context_values else None

        queries = self._setup_queries(
            context=context,
            context_path=getattr(data_requirement, 'contextKeyElement', None),
            context_value=context_value,
            data_type=data_type,
            template_id=getattr(data_requirement, 'template', None),
            code_filters=code_filters,
            date_filters=date_filters,
        )

        # Convert to query strings
        return [str(q) for q in queries]

    def _extract_code_filters(self, data_requirement: Any) -> List[Any]:
        """Extract code filters from data requirement.

        Args:
            data_requirement: Data requirement

        Returns:
            List of code filters
        """
        code_filters = []
        if hasattr(data_requirement, 'codeFilter'):
            code_filters = data_requirement.codeFilter or []
        return code_filters

    def _extract_date_filters(self, data_requirement: Any) -> List[Any]:
        """Extract date filters from data requirement.

        Args:
            data_requirement: Data requirement

        Returns:
            List of date filters
        """
        date_filters = []
        if hasattr(data_requirement, 'dateFilter'):
            date_filters = data_requirement.dateFilter or []
        return date_filters
