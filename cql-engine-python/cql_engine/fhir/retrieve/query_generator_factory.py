"""Factory for creating FHIR query generators."""

from typing import Any, Optional

from .base_query_generator import BaseFhirQueryGenerator
from .dstu3_query_generator import Dstu3FhirQueryGenerator
from .r4_query_generator import R4FhirQueryGenerator
from .version_integrity_checker import FhirVersionEnum
from .search_parameter_resolver import SearchParameterResolver
from ..exception import FhirVersionMismatchException


class FhirQueryGeneratorFactory:
    """Factory for creating version-specific FHIR query generators."""

    @staticmethod
    def create(
        model_resolver: Any,
        search_parameter_resolver: SearchParameterResolver,
        terminology_provider: Optional[Any],
    ) -> BaseFhirQueryGenerator:
        """Create a FHIR query generator for the given FHIR version.

        Args:
            model_resolver: Model resolver for the FHIR version
            search_parameter_resolver: Search parameter resolver
            terminology_provider: Terminology provider

        Returns:
            Appropriate query generator for the FHIR version

        Raises:
            ValueError: If the FHIR version is not supported
        """
        try:
            fhir_version = FhirQueryGeneratorFactory._fetch_fhir_version(
                search_parameter_resolver
            )

            if fhir_version == FhirVersionEnum.DSTU3:
                return Dstu3FhirQueryGenerator(
                    search_parameter_resolver, terminology_provider, model_resolver
                )
            elif fhir_version == FhirVersionEnum.R4:
                return R4FhirQueryGenerator(
                    search_parameter_resolver, terminology_provider, model_resolver
                )
            else:
                raise ValueError(
                    f"Unsupported FHIR version for FHIR Query Generation: {fhir_version}"
                )
        except FhirVersionMismatchException:
            raise
        except Exception as e:
            raise ValueError(f"Error creating FHIR query generator: {str(e)}")

    @staticmethod
    def create_with_options(
        model_resolver: Any,
        search_parameter_resolver: SearchParameterResolver,
        terminology_provider: Optional[Any],
        should_expand_value_sets: Optional[bool] = None,
        max_codes_per_query: Optional[int] = None,
        page_size: Optional[int] = None,
        query_batch_threshold: Optional[int] = None,
    ) -> BaseFhirQueryGenerator:
        """Create a FHIR query generator with configuration options.

        Args:
            model_resolver: Model resolver
            search_parameter_resolver: Search parameter resolver
            terminology_provider: Terminology provider
            should_expand_value_sets: Whether to expand value sets
            max_codes_per_query: Maximum codes per query
            page_size: Page size for pagination
            query_batch_threshold: Batch threshold for queries

        Returns:
            Configured query generator

        Raises:
            ValueError: If the FHIR version is not supported
        """
        generator = FhirQueryGeneratorFactory.create(
            model_resolver, search_parameter_resolver, terminology_provider
        )

        if should_expand_value_sets is not None:
            generator.expand_value_sets_value = should_expand_value_sets

        if max_codes_per_query is not None:
            generator.max_codes_per_query_value = max_codes_per_query

        if query_batch_threshold is not None:
            generator.query_batch_threshold_value = query_batch_threshold

        if page_size is not None:
            generator.page_size_value = page_size

        return generator

    @staticmethod
    def _fetch_fhir_version(
        search_parameter_resolver: SearchParameterResolver,
    ) -> FhirVersionEnum:
        """Get FHIR version from search parameter resolver.

        Args:
            search_parameter_resolver: Search parameter resolver

        Returns:
            FHIR version

        Raises:
            ValueError: If version cannot be determined
        """
        context = search_parameter_resolver.get_fhir_context()
        return FhirQueryGeneratorFactory._fetch_fhir_version_from_context(context)

    @staticmethod
    def _fetch_fhir_version_from_context(context: Any) -> FhirVersionEnum:
        """Get FHIR version from context.

        Args:
            context: FHIR context

        Returns:
            FHIR version

        Raises:
            ValueError: If version cannot be determined
        """
        if context is None:
            raise ValueError("The provided argument is null")

        try:
            if hasattr(context, "get_version"):
                version = context.get_version()
                if hasattr(version, "get_version"):
                    version_str = version.get_version()
                    if hasattr(version_str, "value"):
                        version_str = version_str.value

                    version_str = str(version_str).upper()
                    # Handle version strings like "3.0.1" -> "DSTU3"
                    if version_str.startswith("3"):
                        return FhirVersionEnum.DSTU3
                    elif version_str.startswith("4"):
                        return FhirVersionEnum.R4
                    elif version_str == "DSTU3":
                        return FhirVersionEnum.DSTU3
                    elif version_str == "R4":
                        return FhirVersionEnum.R4

            # Try enum value directly
            return FhirVersionEnum[version_str]
        except (KeyError, AttributeError, ValueError):
            pass

        raise ValueError("Could not determine FHIR version from context")
