"""
Namespace helper utilities for CQL engine.

Provides utilities for parsing namespace-qualified names.
"""

from typing import Optional


class NamespaceHelper:
    """
    Utility class for parsing namespace-qualified names.

    Provides methods to extract the namespace (URI) and local name parts
    from fully qualified identifiers.
    """

    @staticmethod
    def get_uri_part(namespace_qualified_name: Optional[str]) -> Optional[str]:
        """
        Get the namespace (URI) part of a fully qualified name.

        Returns None if the name is not qualified by namespace.
        The URI part is everything before the last forward slash.

        Examples:
            "http://example.com/Patient" -> "http://example.com"
            "Patient" -> None

        Args:
            namespace_qualified_name: The fully qualified name

        Returns:
            The namespace/URI part, or None if not qualified
        """
        if namespace_qualified_name is None:
            return None

        last_slash = namespace_qualified_name.rfind('/')
        if last_slash > 0:
            return namespace_qualified_name[:last_slash]

        return None

    @staticmethod
    def get_name_part(namespace_qualified_name: Optional[str]) -> Optional[str]:
        """
        Get the local name part of a fully qualified name.

        The name part is everything after the last forward slash.
        If there is no forward slash, the entire string is returned as the name part.

        Examples:
            "http://example.com/Patient" -> "Patient"
            "Patient" -> "Patient"
            "http://example.com/" -> ""

        Args:
            namespace_qualified_name: The fully qualified name

        Returns:
            The local name part, or None if input is None
        """
        if namespace_qualified_name is None:
            return None

        last_slash = namespace_qualified_name.rfind("/")
        if last_slash > 0:
            return namespace_qualified_name[last_slash + 1:]

        return namespace_qualified_name
