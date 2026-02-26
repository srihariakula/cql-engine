"""Code filter for FHIR retrieval."""

from dataclasses import dataclass, field
from typing import Iterable, Optional

# Assuming Code is from cql_engine runtime
# from cql_engine.runtime import Code


@dataclass
class CodeFilter:
    """Filter for code-based FHIR searches.

    Attributes:
        code_path: Path to the code element in the resource
        codes: Iterable of Code objects to filter by
        value_set: ValueSet URL to filter by
    """

    code_path: Optional[str] = None
    codes: Optional[Iterable] = None  # Iterable[Code]
    value_set: Optional[str] = None

    def get_code_path(self) -> Optional[str]:
        """Get the code path."""
        return self.code_path

    def get_codes(self) -> Optional[Iterable]:
        """Get the codes."""
        return self.codes

    def get_value_set(self) -> Optional[str]:
        """Get the value set."""
        return self.value_set
