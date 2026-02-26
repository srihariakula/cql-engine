"""
Aggregate function evaluators for CQL expressions.

Handles aggregate operations like Count, Sum, Min, Max, Avg, etc.
"""

from abc import ABC
from typing import Any, Optional, List
from decimal import Decimal
from statistics import median, stdev, variance

from cql_engine.execution.context import Context
from cql_engine.execution.exceptions import InvalidOperatorArgument


class AggregateEvaluator(ABC):
    """Base class for aggregate evaluators."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the aggregate operation."""
        raise NotImplementedError


class CountEvaluator(AggregateEvaluator):
    """
    Returns the count of non-null elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> int:
        operand = self.operand_expr.evaluate(context)
        return self.count(operand)

    @staticmethod
    def count(source: Any) -> int:
        """Count non-null elements."""
        if source is None:
            return 0

        if isinstance(source, (list, tuple)):
            return sum(1 for x in source if x is not None)

        if isinstance(source, (set, frozenset)):
            return len(source)

        # Handle iterables
        try:
            count = 0
            for element in source:
                if element is not None:
                    count += 1
            return count
        except TypeError:
            raise InvalidOperatorArgument(
                "count(List<T>)",
                f"count({type(source).__name__})"
            )


class SumEvaluator(AggregateEvaluator):
    """
    Returns the sum of non-null elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.sum(operand)

    @staticmethod
    def sum(source: Any) -> Any:
        """Sum elements."""
        if source is None:
            return None

        if isinstance(source, (list, tuple)):
            total = None
            for element in source:
                if element is None:
                    continue
                if total is None:
                    total = element
                else:
                    total = total + element
            return total

        # Handle iterables
        try:
            total = None
            for element in source:
                if element is None:
                    continue
                if total is None:
                    total = element
                else:
                    total = total + element
            return total
        except TypeError:
            raise InvalidOperatorArgument(
                "sum(List<Integer>), sum(List<Decimal>), or sum(List<Quantity>)",
                f"sum({type(source).__name__})"
            )


class MinEvaluator(AggregateEvaluator):
    """
    Returns the minimum element in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.min(operand, context)

    @staticmethod
    def min(source: Any, context: Context) -> Any:
        """Get minimum element."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "min(List<T>)",
                    f"min({type(source).__name__})"
                )

        # Filter out nulls and find minimum
        non_null = [x for x in elements if x is not None]
        if not non_null:
            return None

        return min(non_null)


class MaxEvaluator(AggregateEvaluator):
    """
    Returns the maximum element in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.max(operand, context)

    @staticmethod
    def max(source: Any, context: Context) -> Any:
        """Get maximum element."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "max(List<T>)",
                    f"max({type(source).__name__})"
                )

        # Filter out nulls and find maximum
        non_null = [x for x in elements if x is not None]
        if not non_null:
            return None

        return max(non_null)


class AvgEvaluator(AggregateEvaluator):
    """
    Returns the average (mean) of elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return self.avg(operand)

    @staticmethod
    def avg(source: Any) -> Optional[Decimal]:
        """Calculate average."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "avg(List<Integer>), avg(List<Decimal>), or avg(List<Quantity>)",
                    f"avg({type(source).__name__})"
                )

        # Filter out nulls
        non_null = [x for x in elements if x is not None]
        if not non_null:
            return None

        total = sum(non_null)
        return Decimal(total) / Decimal(len(non_null))


class MedianEvaluator(AggregateEvaluator):
    """
    Returns the median (middle value) of elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.median(operand)

    @staticmethod
    def median(source: Any) -> Any:
        """Calculate median."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "median(List<Decimal>)",
                    f"median({type(source).__name__})"
                )

        # Filter out nulls and sort
        non_null = sorted([x for x in elements if x is not None])
        if not non_null:
            return None

        return median(non_null)


class ModeEvaluator(AggregateEvaluator):
    """
    Returns the mode (most frequent value) of elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.mode(operand)

    @staticmethod
    def mode(source: Any) -> Any:
        """Calculate mode."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "mode(List<T>)",
                    f"mode({type(source).__name__})"
                )

        # Filter out nulls
        non_null = [x for x in elements if x is not None]
        if not non_null:
            return None

        # Count occurrences
        counts = {}
        for item in non_null:
            counts[item] = counts.get(item, 0) + 1

        # Find most common
        max_count = max(counts.values())
        modes = [k for k, v in counts.items() if v == max_count]

        # Return first mode (arbitrary choice if multiple)
        return modes[0] if modes else None


class VarianceEvaluator(AggregateEvaluator):
    """
    Returns the sample variance of elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return self.variance(operand)

    @staticmethod
    def variance(source: Any) -> Optional[Decimal]:
        """Calculate sample variance."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "variance(List<Decimal>)",
                    f"variance({type(source).__name__})"
                )

        # Filter out nulls
        non_null = [float(x) for x in elements if x is not None]
        if len(non_null) < 2:
            return None

        return Decimal(variance(non_null))


class StdDevEvaluator(AggregateEvaluator):
    """
    Returns the sample standard deviation of elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return self.std_dev(operand)

    @staticmethod
    def std_dev(source: Any) -> Optional[Decimal]:
        """Calculate sample standard deviation."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "stddev(List<Decimal>)",
                    f"stddev({type(source).__name__})"
                )

        # Filter out nulls
        non_null = [float(x) for x in elements if x is not None]
        if len(non_null) < 2:
            return None

        return Decimal(stdev(non_null))


class PopulationVarianceEvaluator(AggregateEvaluator):
    """
    Returns the population variance of elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return self.population_variance(operand)

    @staticmethod
    def population_variance(source: Any) -> Optional[Decimal]:
        """Calculate population variance."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "population_variance(List<Decimal>)",
                    f"population_variance({type(source).__name__})"
                )

        # Filter out nulls
        non_null = [float(x) for x in elements if x is not None]
        if not non_null:
            return None

        mean = sum(non_null) / len(non_null)
        sum_squares = sum((x - mean) ** 2 for x in non_null)
        return Decimal(sum_squares / len(non_null))


class PopulationStdDevEvaluator(AggregateEvaluator):
    """
    Returns the population standard deviation of elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return self.population_std_dev(operand)

    @staticmethod
    def population_std_dev(source: Any) -> Optional[Decimal]:
        """Calculate population standard deviation."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "population_stddev(List<Decimal>)",
                    f"population_stddev({type(source).__name__})"
                )

        # Filter out nulls
        non_null = [float(x) for x in elements if x is not None]
        if not non_null:
            return None

        mean = sum(non_null) / len(non_null)
        sum_squares = sum((x - mean) ** 2 for x in non_null)
        variance_val = sum_squares / len(non_null)
        return Decimal(variance_val ** 0.5)


class AllTrueEvaluator(AggregateEvaluator):
    """
    Returns true if all non-null elements in the list are true.
    Empty list returns true.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        operand = self.operand_expr.evaluate(context)
        return self.all_true(operand)

    @staticmethod
    def all_true(source: Any) -> Optional[bool]:
        """Check if all elements are true."""
        if source is None:
            return None

        if isinstance(source, (list, tuple)):
            for element in source:
                if element is None:
                    continue
                if not isinstance(element, bool):
                    raise InvalidOperatorArgument(
                        "all_true(List<Boolean>)",
                        f"all_true(List<{type(element).__name__}>)"
                    )
                if not element:
                    return False
            return True

        # Handle iterables
        try:
            for element in source:
                if element is None:
                    continue
                if not isinstance(element, bool):
                    raise InvalidOperatorArgument(
                        "all_true(List<Boolean>)",
                        f"all_true(List<{type(element).__name__}>)"
                    )
                if not element:
                    return False
            return True
        except TypeError:
            raise InvalidOperatorArgument(
                "all_true(List<Boolean>)",
                f"all_true({type(source).__name__})"
            )


class AnyTrueEvaluator(AggregateEvaluator):
    """
    Returns true if any non-null element in the list is true.
    Empty list returns false.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        operand = self.operand_expr.evaluate(context)
        return self.any_true(operand)

    @staticmethod
    def any_true(source: Any) -> Optional[bool]:
        """Check if any element is true."""
        if source is None:
            return None

        if isinstance(source, (list, tuple)):
            for element in source:
                if element is None:
                    continue
                if not isinstance(element, bool):
                    raise InvalidOperatorArgument(
                        "any_true(List<Boolean>)",
                        f"any_true(List<{type(element).__name__}>)"
                    )
                if element:
                    return True
            return False

        # Handle iterables
        try:
            for element in source:
                if element is None:
                    continue
                if not isinstance(element, bool):
                    raise InvalidOperatorArgument(
                        "any_true(List<Boolean>)",
                        f"any_true(List<{type(element).__name__}>)"
                    )
                if element:
                    return True
            return False
        except TypeError:
            raise InvalidOperatorArgument(
                "any_true(List<Boolean>)",
                f"any_true({type(source).__name__})"
            )


class GeometricMeanEvaluator(AggregateEvaluator):
    """
    Returns the geometric mean of elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return self.geometric_mean(operand)

    @staticmethod
    def geometric_mean(source: Any) -> Optional[Decimal]:
        """Calculate geometric mean."""
        if source is None:
            return None

        elements = []
        if isinstance(source, (list, tuple)):
            elements = source
        else:
            try:
                elements = list(source)
            except TypeError:
                raise InvalidOperatorArgument(
                    "geometric_mean(List<Decimal>)",
                    f"geometric_mean({type(source).__name__})"
                )

        # Filter out nulls
        non_null = [float(x) for x in elements if x is not None]
        if not non_null:
            return None

        if any(x <= 0 for x in non_null):
            return None  # Geometric mean undefined for non-positive values

        product = 1
        for x in non_null:
            product *= x

        return Decimal(product ** (1 / len(non_null)))


class ProductEvaluator(AggregateEvaluator):
    """
    Returns the product of all non-null elements in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.product(operand)

    @staticmethod
    def product(source: Any) -> Any:
        """Calculate product."""
        if source is None:
            return None

        if isinstance(source, (list, tuple)):
            result = 1
            for element in source:
                if element is None:
                    continue
                result = result * element
            return result

        # Handle iterables
        try:
            result = 1
            for element in source:
                if element is None:
                    continue
                result = result * element
            return result
        except TypeError:
            raise InvalidOperatorArgument(
                "product(List<Integer>), product(List<Decimal>), or product(List<Quantity>)",
                f"product({type(source).__name__})"
            )
