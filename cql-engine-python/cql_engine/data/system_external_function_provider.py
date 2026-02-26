"""
System external function provider that manages static function evaluation.
"""

from typing import List, Callable
from cql_engine.data.external_function_provider import ExternalFunctionProvider


class SystemExternalFunctionProvider(ExternalFunctionProvider):
    """
    ExternalFunctionProvider implementation that evaluates static functions.

    Maintains a list of static functions that can be called during CQL evaluation.
    """

    def __init__(self, static_functions: List[Callable]):
        """
        Initialize with a list of static functions.

        Args:
            static_functions: List of callable functions/methods to make available
        """
        self.static_functions = static_functions

    def evaluate(self, static_function_name: str, arguments: List[object]) -> object:
        """
        Evaluate a static function by name with the given arguments.

        Args:
            static_function_name: The name of the function to evaluate
            arguments: The arguments to pass to the function

        Returns:
            The result of the function evaluation

        Raises:
            ValueError: If the function cannot be found
            RuntimeError: If the function raises an exception during execution
        """
        for static_function in self.static_functions:
            # Get function name - handle both regular functions and methods
            if hasattr(static_function, '__name__'):
                func_name = static_function.__name__
            else:
                func_name = str(static_function)

            if func_name == static_function_name:
                try:
                    # Call the function with the provided arguments
                    return static_function(*arguments)
                except TypeError as e:
                    raise ValueError(
                        f"Unable to invoke function [{static_function_name}]: {str(e)}"
                    )
                except Exception as e:
                    raise RuntimeError(
                        f"Error when executing function [{static_function_name}]: {str(e)}"
                    )

        raise ValueError(f"Unable to find function [{static_function_name}].")
