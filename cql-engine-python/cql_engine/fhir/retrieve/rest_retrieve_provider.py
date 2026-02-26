"""REST-based FHIR retrieve provider."""

from typing import Any, Dict, Iterable, List, Optional
import requests

from .search_parameter_map import SearchParameterMap
from .search_parameter_resolver import SearchParameterResolver
from .search_param_retrieve_provider import SearchParamFhirRetrieveProvider
from .bundle_cursor import FhirBundleCursor


class RestFhirRetrieveProvider(SearchParamFhirRetrieveProvider):
    """FHIR retrieve provider using REST HTTP calls.

    Makes HTTP requests to a FHIR server to retrieve resources based on
    search parameters.
    """

    DEFAULT_SEARCH_STYLE = "GET"

    def __init__(
        self,
        search_parameter_resolver: SearchParameterResolver,
        base_url: str,
        model_resolver: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize the REST retrieve provider.

        Args:
            search_parameter_resolver: Search parameter resolver
            base_url: Base URL of FHIR server (e.g., https://fhir.example.com)
            model_resolver: Optional model resolver
            headers: Optional HTTP headers
        """
        super().__init__(search_parameter_resolver, model_resolver)
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {"Accept": "application/fhir+json"}
        self.search_style = self.DEFAULT_SEARCH_STYLE
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def set_search_style(self, value: str) -> None:
        """Set the search style (GET or POST).

        Args:
            value: Search style
        """
        self.search_style = value

    def get_search_style(self) -> str:
        """Get the search style.

        Returns:
            Search style
        """
        return self.search_style

    def _execute_queries(
        self, data_type: str, queries: List[SearchParameterMap]
    ) -> Iterable[Any]:
        """Execute search queries via REST.

        Args:
            data_type: FHIR resource type
            queries: List of search parameter maps

        Returns:
            Iterable of resources
        """
        if not queries:
            return []

        resources = []
        bundles = []

        for query_map in queries:
            result = self._execute_query(data_type, query_map)
            if result:
                if self._is_bundle(result):
                    bundles.append(result)
                else:
                    resources.append(result)

        # Process bundles with pagination
        for bundle in bundles:
            cursor = FhirBundleCursor(self.session, bundle, data_type)
            for resource in cursor:
                resources.append(resource)

        return resources

    def _execute_query(
        self, data_type: str, query_map: SearchParameterMap
    ) -> Optional[Any]:
        """Execute a single query.

        Args:
            data_type: FHIR resource type
            query_map: Search parameter map

        Returns:
            Bundle or single resource
        """
        # Check for ID-based query
        if query_map.contains_key("_id"):
            return self._query_by_id(data_type, query_map)

        # Build search URL
        url = f"{self.base_url}/{data_type}"

        # Convert search map to query parameters
        params = self._build_query_params(query_map)

        try:
            if self.search_style == "GET":
                response = self.session.get(url, params=params)
            else:  # POST
                response = self.session.post(url, data=params)

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error executing FHIR query: {e}")
            return None

    def _query_by_id(
        self, data_type: str, query_map: SearchParameterMap
    ) -> Optional[Any]:
        """Query for a resource by ID.

        Args:
            data_type: Resource type
            query_map: Map containing _id parameter

        Returns:
            Resource, or None if not found
        """
        id_params = query_map.get("_id")
        if not id_params:
            return None

        # Get the first ID value
        resource_id = None
        for param_list in id_params:
            for param in param_list:
                if hasattr(param, "value"):
                    resource_id = param.value
                elif isinstance(param, str):
                    resource_id = param
                if resource_id:
                    break
            if resource_id:
                break

        if not resource_id:
            return None

        # Query by ID
        url = f"{self.base_url}/{data_type}/{resource_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching resource by ID: {e}")
            return None

    def _build_query_params(self, query_map: SearchParameterMap) -> Dict[str, str]:
        """Build HTTP query parameters from search map.

        Args:
            query_map: Search parameter map

        Returns:
            Dictionary of query parameters
        """
        params = {}

        for param_name, param_lists in query_map.entry_set():
            if not param_name:
                continue

            values = []
            for param_list in param_lists:
                for param in param_list:
                    if hasattr(param, "get_value_as_query_token"):
                        values.append(param.get_value_as_query_token())
                    elif hasattr(param, "value"):
                        values.append(str(param.value))
                    elif isinstance(param, (list, tuple)):
                        # Handle tuples from code parameters
                        if len(param) == 2 and param[0]:
                            values.append(f"{param[0]}|{param[1]}")
                        else:
                            values.append(str(param[1]) if len(param) > 1 else str(param[0]))
                    else:
                        values.append(str(param))

            if values:
                params[param_name] = ",".join(values)

        # Add count if specified
        if query_map.count:
            params["_count"] = str(query_map.count)

        # Add summary if specified
        if query_map.summary_mode:
            params["_summary"] = query_map.summary_mode

        return params

    @staticmethod
    def _is_bundle(obj: Any) -> bool:
        """Check if an object is a FHIR Bundle.

        Args:
            obj: Object to check

        Returns:
            True if object is a Bundle
        """
        if isinstance(obj, dict):
            return obj.get("resourceType") == "Bundle"
        if hasattr(obj, "resource_type"):
            return obj.resource_type == "Bundle"
        return False

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "RestFhirRetrieveProvider":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
