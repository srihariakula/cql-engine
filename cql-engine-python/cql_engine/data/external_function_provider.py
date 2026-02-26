"""
External function provider interface for CQL engine.

Allows evaluation of external/static functions during CQL evaluation.
"""

from abc import ABC, abstractmethod
from typing import List


class ExternalFunctionProvider(ABC):
    """
    Interface for evaluating external/static functions during CQL evaluation.
    """

    @abstractmethod
    def evaluate(self, static_function_name: str, arguments: List[object]) -> object:
        """
        Evaluate an external/static function.

        Args:
            static_function_name: The name of the function to evaluate
            arguments: The arguments to pass to the function

        Returns:
            The result of the function evaluation

        Raises:
            ValueError: If the function cannot be found or evaluated
        """
        pass
