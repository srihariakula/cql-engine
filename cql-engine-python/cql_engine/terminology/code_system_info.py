"""
Code system information for CQL engine.
"""

from typing import Optional
from cql_engine.runtime.code_system import CodeSystem


class CodeSystemInfo:
    """
    Information about a code system.

    Encapsulates the identity and version of a code system used during CQL evaluation.
    """

    @staticmethod
    def from_code_system(code_system: CodeSystem) -> 'CodeSystemInfo':
        """
        Create a CodeSystemInfo from a CodeSystem object.

        Args:
            code_system: The CodeSystem to create info from

        Returns:
            A new CodeSystemInfo instance
        """
        return CodeSystemInfo().with_id(code_system.get_id()).with_version(code_system.get_version())

    def __init__(self):
        """Initialize the code system info."""
        self.id: Optional[str] = None
        self.version: Optional[str] = None

    def get_id(self) -> Optional[str]:
        """
        Get the code system identifier.

        Returns:
            The code system ID
        """
        return self.id

    def set_id(self, code_system_id: str) -> None:
        """
        Set the code system identifier.

        Args:
            code_system_id: The code system ID
        """
        self.id = code_system_id

    def with_id(self, code_system_id: str) -> 'CodeSystemInfo':
        """
        Set the code system identifier and return self for method chaining.

        Args:
            code_system_id: The code system ID

        Returns:
            Self for method chaining
        """
        self.set_id(code_system_id)
        return self

    def get_version(self) -> Optional[str]:
        """
        Get the code system version.

        Returns:
            The code system version
        """
        return self.version

    def set_version(self, version: str) -> None:
        """
        Set the code system version.

        Args:
            version: The code system version
        """
        self.version = version

    def with_version(self, version: str) -> 'CodeSystemInfo':
        """
        Set the code system version and return self for method chaining.

        Args:
            version: The code system version

        Returns:
            Self for method chaining
        """
        self.set_version(version)
        return self
