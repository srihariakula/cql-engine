"""Bundle cursor for iterating FHIR search results."""

from typing import Any, Iterator, List, Optional

from .search_parameter_resolver import SearchParameterResolver
from ..exception import UnknownElement


class FhirBundleCursor:
    """Cursor for iterating through FHIR Bundle search results.

    Handles pagination through FHIR bundles and filters results by resource type
    and profile conformance.
    """

    def __init__(
        self,
        fhir_client: Any,
        results: Any,
        data_type: Optional[str] = None,
        template_id: Optional[str] = None,
    ) -> None:
        """Initialize the cursor.

        Args:
            fhir_client: FHIR client for paginated requests
            results: Initial FHIR Bundle
            data_type: Optional filter by resource type
            template_id: Optional filter by StructureDefinition profile
        """
        self.fhir_client = fhir_client
        self.results = results
        self.data_type = data_type
        self.template_id = template_id

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator over bundle entries.

        Returns:
            Iterator yielding FHIR resources
        """
        return FhirBundleIterator(
            self.fhir_client, self.results, self.data_type, self.template_id
        )


class FhirBundleIterator(Iterator):
    """Iterator for FHIR Bundle entries.

    Handles filtering by resource type and profile, with pagination support.
    """

    def __init__(
        self,
        fhir_client: Any,
        results: Any,
        data_type: Optional[str] = None,
        template_id: Optional[str] = None,
    ) -> None:
        """Initialize the iterator.

        Args:
            fhir_client: FHIR client
            results: Initial bundle
            data_type: Resource type filter
            template_id: Profile filter
        """
        self.fhir_client = fhir_client
        self.results = results
        self.data_type = data_type
        self.template_id = template_id
        self.current = -1
        self.data_type_class = None
        self.current_entry: List[Any] = []

        # Don't filter by base resource profiles
        if (
            self.template_id
            and self.data_type
            and self.template_id.startswith(
                f"http://hl7.org/fhir/StructureDefinition/{data_type}"
            )
        ):
            self.template_id = None

        # Get the data type class for filtering
        if data_type:
            try:
                resource_def = fhir_client.get_fhir_context().get_resource_definition(
                    data_type
                )
                if resource_def:
                    self.data_type_class = resource_def.get_implementing_class()
            except Exception:
                pass

        self.current_entry = self._get_entry()

    def __iter__(self) -> "FhirBundleIterator":
        """Return self as iterator."""
        return self

    def __next__(self) -> Any:
        """Get the next entry.

        Returns:
            Next FHIR resource

        Raises:
            StopIteration: When no more entries
            UnknownElement: If iteration error occurs
        """
        self.current += 1

        if self.current < len(self.current_entry):
            return self.current_entry[self.current]

        # Load next page if available
        next_link = self._get_link()
        if next_link:
            try:
                self.results = (
                    self.fhir_client.load_page().next(self.results).execute()
                )
                self.current_entry = self._get_entry()
                self.current = 0

                if self.current < len(self.current_entry):
                    return self.current_entry[self.current]
            except Exception as e:
                raise UnknownElement(f"Error loading next page: {str(e)}")

        raise StopIteration

    def has_next(self) -> bool:
        """Check if there are more entries.

        Returns:
            True if more entries exist
        """
        return (
            self.current < len(self.current_entry) - 1 or self._get_link() is not None
        )

    def _get_entry(self) -> List[Any]:
        """Get entries from current bundle.

        Returns:
            List of entries matching filters
        """
        try:
            if self.data_type_class:
                # Filter by resource type
                entries = self._get_entries_of_type(
                    self.fhir_client.get_fhir_context(), self.results, self.data_type_class
                )

                # Filter by template/profile if specified
                if self.template_id:
                    return self._get_trusted_entries(entries, self.template_id)
                return entries
            else:
                # Return all entries
                return self._get_all_entries(self.fhir_client.get_fhir_context(), self.results)
        except Exception:
            return []

    def _get_trusted_entries(self, entries: List[Any], template_id: str) -> List[Any]:
        """Filter entries by conformance to a profile.

        Args:
            entries: List of resources
            template_id: Profile URL to match

        Returns:
            Filtered list of resources
        """
        trusted_entries = []
        for entry in entries:
            try:
                # Check if resource has meta.profile
                if hasattr(entry, "meta") and entry.meta:
                    profiles = entry.meta.get("profile", [])
                    if isinstance(profiles, list):
                        for profile in profiles:
                            profile_value = (
                                profile.get("value")
                                if isinstance(profile, dict)
                                else str(profile)
                            )
                            if profile_value == template_id:
                                trusted_entries.append(entry)
                                break
            except Exception:
                pass

        return trusted_entries

    def _get_entries_of_type(
        self, context: Any, bundle: Any, data_type_class: type
    ) -> List[Any]:
        """Get bundle entries of a specific type.

        Args:
            context: FHIR context
            bundle: Bundle resource
            data_type_class: Resource type class to filter by

        Returns:
            List of matching entries
        """
        entries = []

        try:
            # Try to extract entries from bundle
            if hasattr(bundle, "entry"):
                for entry_wrapper in bundle.entry:
                    if hasattr(entry_wrapper, "resource"):
                        resource = entry_wrapper.resource
                        if isinstance(resource, data_type_class):
                            entries.append(resource)
            elif hasattr(bundle, "get") and callable(bundle.get):
                # Handle dict-like bundle
                entry_list = bundle.get("entry", [])
                for entry in entry_list:
                    resource = entry.get("resource") if isinstance(entry, dict) else None
                    if resource and isinstance(resource, data_type_class):
                        entries.append(resource)
        except Exception:
            pass

        return entries

    def _get_all_entries(self, context: Any, bundle: Any) -> List[Any]:
        """Get all entries from bundle.

        Args:
            context: FHIR context
            bundle: Bundle resource

        Returns:
            List of all entries
        """
        entries = []

        try:
            if hasattr(bundle, "entry"):
                for entry_wrapper in bundle.entry:
                    if hasattr(entry_wrapper, "resource"):
                        entries.append(entry_wrapper.resource)
            elif hasattr(bundle, "get") and callable(bundle.get):
                entry_list = bundle.get("entry", [])
                for entry in entry_list:
                    resource = entry.get("resource") if isinstance(entry, dict) else None
                    if resource:
                        entries.append(resource)
        except Exception:
            pass

        return entries

    def _get_link(self) -> Optional[str]:
        """Get the next link from bundle.

        Returns:
            URL of next page, or None if not available
        """
        try:
            if hasattr(self.results, "link"):
                for link in self.results.link:
                    if hasattr(link, "relation"):
                        if link.relation == "next":
                            return link.get("url") if hasattr(link, "get") else link.url
        except Exception:
            pass

        return None
