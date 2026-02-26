"""
Terminology provider interface for CQL engine.

Provides access to code systems and value sets during CQL evaluation.
"""

from abc import ABC, abstractmethod
from typing import Iterable
from cql_engine.runtime.code import Code


class CodeSystemInfo:
    """Placeholder - defined in code_system_info module."""
    pass


class ValueSetInfo:
    """Placeholder - defined in value_set_info module."""
    pass


class TerminologyProvider(ABC):
    """
    Interface for terminology operations during CQL evaluation.

    Provides access to code systems, value sets, and terminology validation.
    """

    @abstractmethod
    def in_value_set(self, code: Code, value_set: 'ValueSetInfo') -> bool:
        """
        Check if a given Code is a member of a given ValueSet.

        Args:
            code: The code to check
            value_set: The value set to check membership in

        Returns:
            True if code is a member of the ValueSet, False otherwise

        Raises:
            Exception: If there's an error during the membership check
        """
        pass

    @abstractmethod
    def expand(self, value_set: 'ValueSetInfo') -> Iterable[Code]:
        """
        Expand the set of Codes for a given ValueSet.

        Args:
            value_set: The ValueSet to expand

        Returns:
            An iterable of Codes in the ValueSet

        Raises:
            Exception: If there's an error during expansion
        """
        pass

    @abstractmethod
    def lookup(self, code: Code, code_system: CodeSystemInfo) -> Code:
        """
        Look up the display value for a given Code from a given CodeSystem.

        Args:
            code: The Code to look up
            code_system: The CodeSystem to look up in

        Returns:
            The Code with the display value filled

        Raises:
            Exception: If there's an error during lookup
        """
        pass
