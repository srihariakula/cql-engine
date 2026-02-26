"""Search parameter map for FHIR queries."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class EverythingModeEnum(Enum):
    """Enum for Everything Mode in search."""

    ENCOUNTER_INSTANCE = ("ENCOUNTER_INSTANCE", True, False, True)
    ENCOUNTER_TYPE = ("ENCOUNTER_TYPE", True, False, False)
    PATIENT_INSTANCE = ("PATIENT_INSTANCE", False, True, True)
    PATIENT_TYPE = ("PATIENT_TYPE", False, True, False)

    def __init__(self, name: str, is_encounter: bool, is_patient: bool, is_instance: bool):
        """Initialize the enum."""
        self.name = name
        self._is_encounter = is_encounter
        self._is_patient = is_patient
        self._is_instance = is_instance

    def is_encounter(self) -> bool:
        """Check if this is encounter mode."""
        return self._is_encounter

    def is_patient(self) -> bool:
        """Check if this is patient mode."""
        return self._is_patient

    def is_instance(self) -> bool:
        """Check if this is instance mode."""
        return self._is_instance


@dataclass
class SearchParameterMap:
    """Map of search parameters for FHIR queries.

    This represents the HAPI FHIR SearchParameterMap adapted for Python.
    It stores query parameters in a nested structure: name -> AND list -> OR list -> parameter
    """

    # Internal storage: name -> List[List[IQueryParameterType]]
    _search_parameter_map: Dict[str, List[List[Any]]] = field(default_factory=dict)

    # Additional properties
    count: Optional[int] = None
    everything_mode: Optional[EverythingModeEnum] = None
    includes: Set[str] = field(default_factory=set)
    last_updated: Optional[Any] = None  # DateRangeParam
    load_synchronous: bool = False
    load_synchronous_up_to: Optional[int] = None
    rev_includes: Set[str] = field(default_factory=set)
    sort: Optional[Any] = None  # SortSpec
    summary_mode: Optional[str] = None
    search_total_mode: Optional[str] = None

    def add(self, name: str, param: Any) -> "SearchParameterMap":
        """Add a parameter to the map.

        Args:
            name: Parameter name
            param: Query parameter (can be IQueryParameterType, IQueryParameterOr, or IQueryParameterAnd)

        Returns:
            self for method chaining
        """
        if param is None:
            return self

        if name not in self._search_parameter_map:
            self._search_parameter_map[name] = []

        # Handle different parameter types
        if hasattr(param, "get_values_as_query_tokens"):
            # IQueryParameterOr or IQueryParameterAnd
            param_list = list(param.get_values_as_query_tokens())
            if param_list:
                self._search_parameter_map[name].append(param_list)
        else:
            # Single parameter
            self._search_parameter_map[name].append([param])

        return self

    def get(self, name: str) -> Optional[List[List[Any]]]:
        """Get parameters by name.

        Args:
            name: Parameter name

        Returns:
            List of AND-separated parameter lists, or None if not found
        """
        return self._search_parameter_map.get(name)

    def contains_key(self, name: str) -> bool:
        """Check if a parameter name exists.

        Args:
            name: Parameter name

        Returns:
            True if the parameter exists
        """
        return name in self._search_parameter_map

    def remove(self, name: str) -> Optional[List[List[Any]]]:
        """Remove a parameter by name.

        Args:
            name: Parameter name

        Returns:
            The removed parameter list, or None if not found
        """
        return self._search_parameter_map.pop(name, None)

    def key_set(self) -> Set[str]:
        """Get all parameter names.

        Returns:
            Set of parameter names
        """
        return set(self._search_parameter_map.keys())

    def is_empty(self) -> bool:
        """Check if the map is empty.

        Returns:
            True if no parameters are stored
        """
        return len(self._search_parameter_map) == 0

    def entry_set(self) -> List[tuple]:
        """Get all entries as (name, parameters) tuples.

        Returns:
            List of (name, List[List[param]]) tuples
        """
        return list(self._search_parameter_map.items())

    def values(self) -> List[List[List[Any]]]:
        """Get all parameter values.

        Returns:
            List of parameter lists
        """
        return list(self._search_parameter_map.values())

    def clean(self) -> None:
        """Remove empty parameters from the map."""
        names_to_remove = []

        for name, and_or_params in self._search_parameter_map.items():
            for and_list_idx in range(len(and_or_params) - 1, -1, -1):
                next_or_list = and_or_params[and_list_idx]

                for or_list_idx in range(len(next_or_list) - 1, -1, -1):
                    next_or = next_or_list[or_list_idx]

                    # Check if parameter has no value
                    has_no_value = False
                    if hasattr(next_or, "get_missing") and next_or.get_missing() is not None:
                        continue
                    if (
                        hasattr(next_or, "get_value_as_string")
                        and not next_or.get_value_as_string()
                    ):
                        has_no_value = True

                    if has_no_value:
                        next_or_list.pop(or_list_idx)

                if len(next_or_list) == 0:
                    and_or_params.pop(and_list_idx)

        # Remove empty parameter names
        for name in list(self._search_parameter_map.keys()):
            if len(self._search_parameter_map[name]) == 0:
                names_to_remove.append(name)

        for name in names_to_remove:
            del self._search_parameter_map[name]

    def to_normalized_query_string(self) -> str:
        """Convert to a normalized query string.

        Returns:
            Query string representation
        """
        params = []
        for name in sorted(self._search_parameter_map.keys()):
            and_or_params = self._search_parameter_map[name]
            for param_list in and_or_params:
                for param in param_list:
                    if hasattr(param, "get_value_as_query_token"):
                        value = param.get_value_as_query_token()
                        params.append(f"{name}={value}")

        if self.count is not None:
            params.append(f"_count={self.count}")

        if self.summary_mode is not None:
            params.append(f"_summary={self.summary_mode}")

        if self.search_total_mode is not None:
            params.append(f"_total={self.search_total_mode}")

        return "?" + "&".join(params) if params else "?"

    def __str__(self) -> str:
        """String representation."""
        return str(self._search_parameter_map)

    def __repr__(self) -> str:
        """Repr."""
        return f"SearchParameterMap({self._search_parameter_map})"
