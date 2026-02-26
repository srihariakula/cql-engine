"""
Value set information for CQL engine.
"""

from typing import List, Optional
from cql_engine.terminology.code_system_info import CodeSystemInfo
from cql_engine.runtime.value_set import ValueSet


class ValueSetInfo:
    """
    Information about a value set.

    Encapsulates the identity, version, and associated code systems for a value set
    used during CQL evaluation.
    """

    @staticmethod
    def from_value_set(value_set: ValueSet) -> 'ValueSetInfo':
        """
        Create a ValueSetInfo from a ValueSet object.

        Args:
            value_set: The ValueSet to create info from

        Returns:
            A new ValueSetInfo instance
        """
        vsi = ValueSetInfo().with_id(value_set.get_id()).with_version(value_set.get_version())
        for code_system in value_set.get_code_systems():
            vsi.with_code_system(CodeSystemInfo.from_code_system(code_system))
        return vsi

    def __init__(self):
        """Initialize the value set info."""
        self.id: Optional[str] = None
        self.version: Optional[str] = None
        self.code_systems: List[CodeSystemInfo] = []

    def get_id(self) -> Optional[str]:
        """
        Get the value set identifier.

        Returns:
            The value set ID
        """
        return self.id

    def set_id(self, value_set_id: str) -> None:
        """
        Set the value set identifier.

        Args:
            value_set_id: The value set ID
        """
        self.id = value_set_id

    def with_id(self, value_set_id: str) -> 'ValueSetInfo':
        """
        Set the value set identifier and return self for method chaining.

        Args:
            value_set_id: The value set ID

        Returns:
            Self for method chaining
        """
        self.set_id(value_set_id)
        return self

    def get_version(self) -> Optional[str]:
        """
        Get the value set version.

        Returns:
            The value set version
        """
        return self.version

    def set_version(self, version: str) -> None:
        """
        Set the value set version.

        Args:
            version: The value set version
        """
        self.version = version

    def with_version(self, version: str) -> 'ValueSetInfo':
        """
        Set the value set version and return self for method chaining.

        Args:
            version: The value set version

        Returns:
            Self for method chaining
        """
        self.set_version(version)
        return self

    def get_code_systems(self) -> List[CodeSystemInfo]:
        """
        Get the code systems associated with this value set.

        Returns:
            List of associated CodeSystemInfo objects
        """
        return self.code_systems

    def with_code_system(self, code_system: CodeSystemInfo) -> 'ValueSetInfo':
        """
        Add a code system to this value set and return self for method chaining.

        Args:
            code_system: The CodeSystemInfo to add

        Returns:
            Self for method chaining
        """
        self.code_systems.append(code_system)
        return self
