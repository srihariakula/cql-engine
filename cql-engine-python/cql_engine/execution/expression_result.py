"""
Expression result class for CQL engine execution.

Represents the result of evaluating a single CQL expression.
"""

from typing import List, Optional


class ExpressionResult:
    """
    Represents the result of evaluating a single CQL expression.

    Encapsulates the computed value and the resources that were evaluated
    to produce that value.
    """

    def __init__(self, value: Optional[object], evaluated_resources: Optional[List[object]] = None):
        """
        Initialize an expression result.

        Args:
            value: The computed value of the expression
            evaluated_resources: The resources evaluated to produce this value
        """
        self.value = value
        self.evaluated_resources = evaluated_resources or []

    def value(self) -> Optional[object]:
        """
        Get the computed value of the expression.

        Returns:
            The expression value
        """
        return self.value

    def evaluated_resources(self) -> List[object]:
        """
        Get the resources that were evaluated to produce this result.

        Returns:
            List of evaluated resources
        """
        return self.evaluated_resources
