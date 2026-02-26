"""
Debug Result Entry

Stores a single debug result value.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class DebugResultEntry:
    """
    Stores a single debug result value.

    Records the value that was produced at a specific debug point.
    """

    value: Optional[Any]

    def get_value(self) -> Optional[Any]:
        """
        Get the debug result value.

        Returns:
            The value that was produced
        """
        return self.value
