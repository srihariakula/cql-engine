"""
Evaluation result class for CQL engine execution.

Represents the results of evaluating a CQL library.
"""

from typing import Dict, Optional
from collections import OrderedDict
from cql_engine.execution.expression_result import ExpressionResult


class DebugResult:
    """Placeholder - defined in debug module."""
    pass


class EvaluationResult:
    """
    Represents the result of evaluating a CQL library.

    Contains the results of evaluating each expression in the library,
    along with optional debug information.
    """

    def __init__(self):
        """Initialize an empty evaluation result."""
        self.expression_results: Dict[str, ExpressionResult] = OrderedDict()
        self.debug_result: Optional[DebugResult] = None

    def for_expression(self, expression_name: str) -> Optional[ExpressionResult]:
        """
        Get the result for a specific expression by name.

        Args:
            expression_name: The name of the expression

        Returns:
            The ExpressionResult for that expression, or None if not found
        """
        return self.expression_results.get(expression_name)

    def get_debug_result(self) -> Optional[DebugResult]:
        """
        Get the debug result.

        Returns:
            The DebugResult or None if no debug result was generated
        """
        return self.debug_result

    def set_debug_result(self, debug_result: DebugResult) -> None:
        """
        Set the debug result.

        Args:
            debug_result: The DebugResult to set
        """
        self.debug_result = debug_result
