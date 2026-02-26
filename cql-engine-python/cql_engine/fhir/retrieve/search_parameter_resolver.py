"""Search parameter resolver for FHIR."""

from abc import ABC
from typing import Any, Optional, Tuple
from enum import Enum


class RestSearchParameterTypeEnum(Enum):
    """REST search parameter types."""

    TOKEN = "TOKEN"
    REFERENCE = "REFERENCE"
    QUANTITY = "QUANTITY"
    STRING = "STRING"
    NUMBER = "NUMBER"
    URI = "URI"
    DATE = "DATE"
    HAS = "HAS"
    COMPOSITE = "COMPOSITE"


class SearchParameterResolver:
    """Resolves FHIR search parameters.

    This class handles mapping CQL data element paths to FHIR search parameters.
    It requires a FHIR context (from fhirclient or similar library) that provides
    resource definitions and search parameter metadata.
    """

    def __init__(self, fhir_context: Any) -> None:
        """Initialize the resolver.

        Args:
            fhir_context: FHIR context providing resource definitions
        """
        self.context = fhir_context

    def get_fhir_context(self) -> Any:
        """Get the FHIR context.

        Returns:
            The FHIR context
        """
        return self.context

    def get_search_parameter_definition(
        self,
        data_type: str,
        path: str,
        param_type: Optional[RestSearchParameterTypeEnum] = None,
    ) -> Optional[Any]:
        """Get a search parameter definition by type and path.

        Args:
            data_type: FHIR resource type (e.g., 'Patient', 'Observation')
            path: Path to the element in the resource
            param_type: Optional filter by parameter type

        Returns:
            The search parameter definition, or None if not found
        """
        if not data_type or not path:
            return None

        # Special case for system params like 'id'
        name = None
        search_path = path
        if path == "id":
            name = "_id"
            search_path = ""

        try:
            # Get resource definition from context
            resource_def = self.context.get_resource_definition(data_type)
            if not resource_def:
                return None

            params = resource_def.get_search_params()
            if not params:
                return None

            for param in params:
                # If name matches, it's the one we want
                if name and param.get_name() == name:
                    return param

                # Filter by parameter type if specified
                if param_type and param.get_param_type() != param_type:
                    continue

                # Check path match
                normalized_path = self._normalize_path(param.get_path())
                if (
                    search_path == normalized_path
                    or search_path.lower() == param.get_name().lower()
                ):
                    return param

        except Exception:
            pass

        return None

    def create_search_parameter(
        self, context: str, data_type: str, path: str, value: str
    ) -> Optional[Tuple[str, Any]]:
        """Create a search parameter from a value.

        Args:
            context: Context type (e.g., 'Patient')
            data_type: FHIR resource type
            path: Path to element
            value: Parameter value

        Returns:
            Tuple of (parameter_name, parameter_object), or None if not found
        """
        search_param = self.get_search_parameter_definition(data_type, path)
        if not search_param:
            return None

        name = search_param.get_name()
        param_type = search_param.get_param_type()

        # Create appropriate parameter type
        if param_type == RestSearchParameterTypeEnum.TOKEN:
            return (name, ("token", value))
        elif param_type == RestSearchParameterTypeEnum.REFERENCE:
            return (name, ("reference", context, value))
        elif param_type == RestSearchParameterTypeEnum.QUANTITY:
            return (name, ("quantity", value))
        elif param_type == RestSearchParameterTypeEnum.STRING:
            return (name, ("string", value))
        elif param_type == RestSearchParameterTypeEnum.NUMBER:
            return (name, ("number", value))
        elif param_type == RestSearchParameterTypeEnum.URI:
            return (name, ("uri", value))

        return None

    @staticmethod
    def _normalize_path(path: Optional[str]) -> str:
        """Normalize a parameter path.

        Args:
            path: Path to normalize

        Returns:
            Normalized path
        """
        if not path:
            return ""

        # Remove [x] suffix used for choice types
        normalized = path.replace("[x]", "")

        # Handle dot notation
        parts = normalized.split(".")
        if len(parts) > 1:
            # Return just the last part for comparison
            return parts[-1].lower()

        return normalized.lower()
