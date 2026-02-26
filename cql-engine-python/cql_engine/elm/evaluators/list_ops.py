"""
List operations evaluators for CQL expressions.

Handles creation and manipulation of lists and their relationships.
"""

from abc import ABC
from typing import Any, Optional, List, Iterable as IterableType

from cql_engine.runtime.interval import Interval
from cql_engine.execution.context import Context
from cql_engine.execution.exceptions import InvalidOperatorArgument


class ListOperationEvaluator(ABC):
    """Base class for list operation evaluators."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the list operation."""
        raise NotImplementedError


class ListEvaluator(ListOperationEvaluator):
    """
    Constructs a list from elements.
    """

    def __init__(self, element_exprs: List[Any]):
        self.element_exprs = element_exprs

    def evaluate(self, context: Context) -> List[Any]:
        result = []
        for element_expr in self.element_exprs:
            result.append(element_expr.evaluate(context))
        return result


class ExistsEvaluator(ListOperationEvaluator):
    """
    Returns true if the list is non-empty (contains at least one non-null element).
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        operand = self.operand_expr.evaluate(context)
        return self.exists(operand)

    @staticmethod
    def exists(source: Any) -> Optional[bool]:
        """Check if list is non-empty."""
        if source is None:
            return False

        if isinstance(source, (list, tuple)):
            return len(source) > 0

        if isinstance(source, IterableType):
            for element in source:
                if element is not None:
                    return True
            return False

        return False


class InEvaluator(ListOperationEvaluator):
    """
    Returns true if a value is in a list or interval.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.in_value(left, right, context)

    @staticmethod
    def in_value(element: Any, source: Any, context: Context) -> Optional[bool]:
        """Check if element is in source list."""
        if element is None or source is None:
            return None

        # Handle Interval
        from cql_engine.runtime.interval import Interval
        if isinstance(source, Interval):
            start = source.get_start()
            end = source.get_end()
            low_closed = source.get_low_closed()
            high_closed = source.get_high_closed()

            if start is not None:
                if low_closed:
                    if element < start:
                        return False
                else:
                    if element <= start:
                        return False

            if end is not None:
                if high_closed:
                    if element > end:
                        return False
                else:
                    if element >= end:
                        return False

            return True

        # Handle List
        if isinstance(source, (list, tuple)):
            for item in source:
                if item == element:
                    return True
            return False

        if isinstance(source, IterableType):
            for item in source:
                if item == element:
                    return True
            return False

        return False


class ContainsEvaluator(ListOperationEvaluator):
    """
    List overload: Returns true if the list contains a value.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.contains(left, right, context)

    @staticmethod
    def contains(source: Any, element: Any, context: Context) -> Optional[bool]:
        """Check if list contains element."""
        return InEvaluator.in_value(element, source, context)


class IncludesEvaluator(ListOperationEvaluator):
    """
    List overload: Returns true if the first list includes all elements of the second list.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.includes(left, right, context)

    @staticmethod
    def includes(left: Any, right: Any, context: Context) -> Optional[bool]:
        """Check if left list includes all elements of right list."""
        if left is None or right is None:
            return None

        if not isinstance(right, (list, tuple, IterableType)):
            raise InvalidOperatorArgument(
                "includes(List<T>, List<T>)",
                f"includes({type(left).__name__}, {type(right).__name__})"
            )

        for element in right:
            if not InEvaluator.in_value(element, left, context):
                return False

        return True


class IncludedInEvaluator(ListOperationEvaluator):
    """
    List overload: Returns true if the first list is included in the second list.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.included_in(left, right, context)

    @staticmethod
    def included_in(left: Any, right: Any, context: Context) -> Optional[bool]:
        """Check if left list is included in right list."""
        # Reverse includes
        return IncludesEvaluator.includes(right, left, context)


class ProperIncludesEvaluator(ListOperationEvaluator):
    """
    List overload: Returns true if first list properly includes second list.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.proper_includes(left, right, context)

    @staticmethod
    def proper_includes(left: Any, right: Any, context: Context) -> Optional[bool]:
        """Check if left properly includes right."""
        if left is None or right is None:
            return None

        # Left properly includes right if it includes it but is not equal
        includes = IncludesEvaluator.includes(left, right, context)
        if includes is None or not includes:
            return includes

        # Check if they're equal (same elements)
        left_list = list(left) if not isinstance(left, list) else left
        right_list = list(right) if not isinstance(right, list) else right

        return left_list != right_list


class ProperIncludedInEvaluator(ListOperationEvaluator):
    """
    List overload: Returns true if first list is properly included in second list.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return ProperIncludesEvaluator.proper_includes(right, left, context)


class UnionEvaluator(ListOperationEvaluator):
    """
    Returns the union of two lists (all elements from both, with duplicates removed).
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Any:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.union(left, right, context)

    @staticmethod
    def union(left: Any, right: Any, context: Context) -> Any:
        """Union two lists."""
        if left is None or right is None:
            return None

        # Handle intervals
        from cql_engine.runtime.interval import Interval
        if isinstance(left, Interval) and isinstance(right, Interval):
            return _union_intervals(left, right, context)

        # Handle lists
        if isinstance(left, (list, tuple)) or isinstance(left, IterableType):
            result = []
            for item in left:
                result.append(item)

            for item in right:
                result.append(item)

            return DistinctEvaluator.distinct(result, context)

        raise InvalidOperatorArgument(
            "union(Interval<T>, Interval<T>) or union(List<T>, List<T>)",
            f"union({type(left).__name__}, {type(right).__name__})"
        )


class IntersectEvaluator(ListOperationEvaluator):
    """
    Returns the intersection of two lists (elements common to both).
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Any:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.intersect(left, right, context)

    @staticmethod
    def intersect(left: Any, right: Any, context: Context) -> Any:
        """Intersect two lists."""
        if left is None or right is None:
            return None

        # Handle intervals
        from cql_engine.runtime.interval import Interval
        if isinstance(left, Interval) and isinstance(right, Interval):
            return _intersect_intervals(left, right, context)

        # Handle lists
        if isinstance(left, (list, tuple)) or isinstance(left, IterableType):
            result = []
            for item in left:
                if InEvaluator.in_value(item, right, context):
                    result.append(item)

            return DistinctEvaluator.distinct(result, context)

        raise InvalidOperatorArgument(
            "intersect(Interval<T>, Interval<T>) or intersect(List<T>, List<T>)",
            f"intersect({type(left).__name__}, {type(right).__name__})"
        )


class ExceptEvaluator(ListOperationEvaluator):
    """
    Returns the set difference (elements in first list but not in second).
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Any:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.except_op(left, right, context)

    @staticmethod
    def except_op(left: Any, right: Any, context: Context) -> Any:
        """Except (set difference) for two lists."""
        if left is None:
            return None

        if right is None and not isinstance(left, Interval):
            return None

        # Handle intervals
        from cql_engine.runtime.interval import Interval
        if isinstance(left, Interval):
            return _except_intervals(left, right, context)

        # Handle lists
        if isinstance(left, (list, tuple)) or isinstance(left, IterableType):
            result = []
            for item in left:
                if not InEvaluator.in_value(item, right, context):
                    result.append(item)

            return DistinctEvaluator.distinct(result, context)

        raise InvalidOperatorArgument(
            "except(Interval<T>, Interval<T>) or except(List<T>, List<T>)",
            f"except({type(left).__name__}, {type(right).__name__})"
        )


class DistinctEvaluator(ListOperationEvaluator):
    """
    Returns the list with duplicates removed.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[List[Any]]:
        operand = self.operand_expr.evaluate(context)
        return self.distinct(operand, context)

    @staticmethod
    def distinct(source: Any, context: Context) -> Optional[List[Any]]:
        """Remove duplicates from list."""
        if source is None:
            return None

        result = []
        for element in source:
            if element is None:
                if not any(item is None for item in result):
                    result.append(None)
                continue

            in_result = InEvaluator.in_value(element, result, context)

            if in_result is None:
                continue

            if not in_result:
                result.append(element)

        return result


class FlattenEvaluator(ListOperationEvaluator):
    """
    Flattens a list of lists into a single list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[List[Any]]:
        operand = self.operand_expr.evaluate(context)
        return self.flatten(operand)

    @staticmethod
    def flatten(source: Any) -> Optional[List[Any]]:
        """Flatten nested lists."""
        if source is None:
            return None

        result = []
        for element in source:
            if isinstance(element, (list, tuple)):
                result.extend(element)
            elif isinstance(element, IterableType) and not isinstance(element, str):
                result.extend(list(element))
            else:
                result.append(element)

        return result


class SingletonFromEvaluator(ListOperationEvaluator):
    """
    Returns the single element from a list with one element.
    Returns null if list is empty or has more than one element.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.singleton_from(operand)

    @staticmethod
    def singleton_from(source: Any) -> Any:
        """Get singleton from list."""
        if source is None:
            return None

        if isinstance(source, (list, tuple)):
            if len(source) == 1:
                return source[0]
            return None

        # Count elements for iterables
        count = 0
        element = None
        for item in source:
            element = item
            count += 1
            if count > 1:
                return None

        return element if count == 1 else None


class IndexerEvaluator(ListOperationEvaluator):
    """
    Returns the element at the specified index in a list.
    """

    def __init__(self, operand_expr, index_expr):
        self.operand_expr = operand_expr
        self.index_expr = index_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        index = self.index_expr.evaluate(context)
        return self.indexer(operand, index)

    @staticmethod
    def indexer(source: Any, index: int) -> Any:
        """Get element by index."""
        if source is None or index is None:
            return None

        if isinstance(source, (list, tuple)):
            if 0 <= index < len(source):
                return source[index]
            return None

        # Convert iterable to list
        source_list = list(source) if isinstance(source, IterableType) else None
        if source_list is not None:
            if 0 <= index < len(source_list):
                return source_list[index]
            return None

        return None


class FirstEvaluator(ListOperationEvaluator):
    """
    Returns the first element in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.first(operand)

    @staticmethod
    def first(source: Any) -> Any:
        """Get first element."""
        if source is None:
            return None

        if isinstance(source, (list, tuple)):
            return source[0] if source else None

        if isinstance(source, IterableType):
            for element in source:
                return element

        return None


class LastEvaluator(ListOperationEvaluator):
    """
    Returns the last element in a list.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.last(operand)

    @staticmethod
    def last(source: Any) -> Any:
        """Get last element."""
        if source is None:
            return None

        if isinstance(source, (list, tuple)):
            return source[-1] if source else None

        if isinstance(source, IterableType):
            result = None
            for element in source:
                result = element
            return result

        return None


class SliceEvaluator(ListOperationEvaluator):
    """
    Returns a slice of a list from startIndex to endIndex (inclusive).
    """

    def __init__(self, operand_expr, start_index_expr, end_index_expr):
        self.operand_expr = operand_expr
        self.start_index_expr = start_index_expr
        self.end_index_expr = end_index_expr

    def evaluate(self, context: Context) -> Optional[List[Any]]:
        operand = self.operand_expr.evaluate(context)
        start_index = self.start_index_expr.evaluate(context)
        end_index = self.end_index_expr.evaluate(context)
        return self.slice(operand, start_index, end_index)

    @staticmethod
    def slice(source: Any, start_index: int, end_index: int) -> Optional[List[Any]]:
        """Slice list."""
        if source is None:
            return None

        if not isinstance(source, (list, tuple)):
            source = list(source) if isinstance(source, IterableType) else None

        if source is None:
            return None

        if start_index is None or end_index is None:
            return None

        # Ensure indices are within bounds
        start = max(0, start_index)
        end = min(len(source), end_index + 1)

        if start >= len(source):
            return []

        return list(source[start:end])


class CurrentEvaluator(ListOperationEvaluator):
    """
    Returns the current item in an iteration context.
    """

    def __init__(self):
        pass

    def evaluate(self, context: Context) -> Any:
        # This requires context-specific implementation
        # Usually set by the iteration context
        return context.get_current_item() if hasattr(context, 'get_current_item') else None


class RepeatEvaluator(ListOperationEvaluator):
    """
    Returns the given element repeated the specified number of times.
    """

    def __init__(self, element_expr, count_expr):
        self.element_expr = element_expr
        self.count_expr = count_expr

    def evaluate(self, context: Context) -> List[Any]:
        element = self.element_expr.evaluate(context)
        count = self.count_expr.evaluate(context)
        return self.repeat(element, count)

    @staticmethod
    def repeat(element: Any, count: int) -> List[Any]:
        """Repeat element count times."""
        if count is None or count < 0:
            return []

        return [element] * count


# Helper functions for interval operations

def _union_intervals(left: Interval, right: Interval, context: Context) -> Optional[Interval]:
    """Union two intervals."""
    from cql_engine.runtime.temporal import BaseTemporal
    from cql_engine.elm.evaluators.interval_ops import OverlapsEvaluator, MeetsEvaluator
    from cql_engine.elm.evaluators.comparison import LessEvaluator, GreaterEvaluator

    left_start = left.get_start()
    left_end = left.get_end()
    right_start = right.get_start()
    right_end = right.get_end()

    if left_start is None or left_end is None or right_start is None or right_end is None:
        return None

    overlaps_or_meets = (
        OverlapsEvaluator.overlaps(left, right, None, context) or
        MeetsEvaluator.meets(left, right, None, context)
    )

    if not overlaps_or_meets:
        return None

    min_val = left_start if LessEvaluator.less(left_start, right_start, context) else right_start
    max_val = left_end if GreaterEvaluator.greater(left_end, right_end, context) else right_end

    return Interval(min_val, True, max_val, True)


def _intersect_intervals(left: Interval, right: Interval, context: Context) -> Optional[Interval]:
    """Intersect two intervals."""
    from cql_engine.elm.evaluators.interval_ops import OverlapsEvaluator
    from cql_engine.elm.evaluators.comparison import GreaterEvaluator, LessEvaluator

    left_start = left.get_start()
    left_end = left.get_end()
    right_start = right.get_start()
    right_end = right.get_end()

    if left_start is None or left_end is None or right_start is None or right_end is None:
        return None

    overlaps = OverlapsEvaluator.overlaps(left, right, None, context)
    if not overlaps:
        return None

    max_start = left_start if GreaterEvaluator.greater(left_start, right_start, context) else right_start
    min_end = left_end if LessEvaluator.less(left_end, right_end, context) else right_end

    return Interval(max_start, max_start is not None, min_end, min_end is not None)


def _except_intervals(left: Interval, right: Interval, context: Context) -> Optional[Interval]:
    """Except (set difference) for intervals."""
    # Simplified implementation - full version in Java is more complex
    if not isinstance(left, Interval) or not isinstance(right, Interval):
        raise InvalidOperatorArgument(
            "except(Interval<T>, Interval<T>)",
            f"except({type(left).__name__}, {type(right).__name__})"
        )

    # Return null for several edge cases (see Java implementation)
    # For now, return a simplified result
    return None
