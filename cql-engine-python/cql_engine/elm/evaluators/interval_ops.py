"""
Interval operations evaluators for CQL expressions.

Handles creation and manipulation of intervals and their relationships.
"""

from abc import ABC
from decimal import Decimal
from typing import Any, Optional, List

from cql_engine.runtime.interval import Interval
from cql_engine.runtime.temporal import BaseTemporal, Date, DateTime, Time, Precision
from cql_engine.execution.context import Context
from cql_engine.execution.exceptions import InvalidOperatorArgument


class IntervalOperationEvaluator(ABC):
    """Base class for interval operation evaluators."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the interval operation."""
        raise NotImplementedError


class IntervalEvaluator(IntervalOperationEvaluator):
    """
    Constructs an interval from low, high, and boundary closure expressions.
    """

    def __init__(self, low_expr=None, high_expr=None, low_closed_expr=None, high_closed_expr=None,
                 low_closed=True, high_closed=True):
        self.low_expr = low_expr
        self.high_expr = high_expr
        self.low_closed_expr = low_closed_expr
        self.high_closed_expr = high_closed_expr
        self.low_closed_default = low_closed
        self.high_closed_default = high_closed

    def evaluate(self, context: Context) -> Optional[Interval]:
        low = self.low_expr.evaluate(context) if self.low_expr else None
        low_closed = (self.low_closed_expr.evaluate(context) if self.low_closed_expr else self.low_closed_default)
        high = self.high_expr.evaluate(context) if self.high_expr else None
        high_closed = (self.high_closed_expr.evaluate(context) if self.high_closed_expr else self.high_closed_default)

        # An interval with no boundaries is not an interval
        if low is None and high is None:
            return None

        return Interval(low, low_closed if low_closed is not None else True,
                       high, high_closed if high_closed is not None else True)


class StartEvaluator(IntervalOperationEvaluator):
    """
    Returns the starting point of an interval.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.start(operand)

    @staticmethod
    def start(operand: Any) -> Any:
        """Get start of interval."""
        if operand is None:
            return None

        if isinstance(operand, Interval):
            return operand.get_start()

        raise InvalidOperatorArgument(
            "start(Interval<T>)",
            f"start({type(operand).__name__})"
        )


class EndEvaluator(IntervalOperationEvaluator):
    """
    Returns the ending point of an interval.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.end(operand)

    @staticmethod
    def end(operand: Any) -> Any:
        """Get end of interval."""
        if operand is None:
            return None

        if isinstance(operand, Interval):
            return operand.get_end()

        raise InvalidOperatorArgument(
            "end(Interval<T>)",
            f"end({type(operand).__name__})"
        )


class ContainsEvaluator(IntervalOperationEvaluator):
    """
    Interval overload for contains operator.
    Returns true if the first interval completely contains the second interval or point.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.contains(left, right, context)

    @staticmethod
    def contains(left: Any, right: Any, context: Context) -> Optional[bool]:
        """Check if left interval contains right value/interval."""
        if left is None or right is None:
            return None

        if isinstance(left, Interval) and isinstance(right, Interval):
            # Check if left contains right interval
            left_start = left.get_start()
            left_end = left.get_end()
            right_start = right.get_start()
            right_end = right.get_end()

            # Both must be contained within left's boundaries
            if not _compare_points(left_start, right_start, left.get_low_closed()) or \
               not _compare_points(right_end, left_end, left.get_high_closed()):
                return False

            return True

        elif isinstance(left, Interval):
            # Check if left interval contains right point
            return _point_in_interval(right, left)

        raise InvalidOperatorArgument(
            "contains(Interval<T>, Interval<T>) or contains(Interval<T>, T)",
            f"contains({type(left).__name__}, {type(right).__name__})"
        )


class InEvaluator(IntervalOperationEvaluator):
    """
    Returns true if a point is in an interval.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.in_interval(left, right)

    @staticmethod
    def in_interval(point: Any, interval: Any) -> Optional[bool]:
        """Check if point is in interval."""
        if point is None or interval is None:
            return None

        if not isinstance(interval, Interval):
            raise InvalidOperatorArgument(
                "in(T, Interval<T>)",
                f"in({type(point).__name__}, {type(interval).__name__})"
            )

        return _point_in_interval(point, interval)


class IncludesEvaluator(IntervalOperationEvaluator):
    """
    Returns true if the first interval completely includes the second interval or point.
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
        """Check if left interval includes right value/interval."""
        # For intervals, includes has same semantics as contains
        return ContainsEvaluator.contains(left, right, context)


class IncludedInEvaluator(IntervalOperationEvaluator):
    """
    Returns true if the first interval is completely included in the second interval.
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
        """Check if left interval is included in right interval."""
        # Reverse contains
        return ContainsEvaluator.contains(right, left, context)


class ProperContainsEvaluator(IntervalOperationEvaluator):
    """
    Returns true if the first interval properly contains the second interval or point.
    Proper means at least one endpoint is different.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.proper_contains(left, right, context)

    @staticmethod
    def proper_contains(left: Any, right: Any, context: Context) -> Optional[bool]:
        """Check if left properly contains right."""
        if left is None or right is None:
            return None

        if isinstance(left, Interval):
            contains = ContainsEvaluator.contains(left, right, context)
            if contains is None or not contains:
                return contains

            # Check if at least one endpoint differs
            if isinstance(right, Interval):
                left_start = left.get_start()
                left_end = left.get_end()
                right_start = right.get_start()
                right_end = right.get_end()

                return (left_start != right_start or left_end != right_end)
            else:
                # For a point, proper contains means the point is strictly inside
                return True

        raise InvalidOperatorArgument(
            "proper_contains(Interval<T>, Interval<T>) or proper_contains(Interval<T>, T)",
            f"proper_contains({type(left).__name__}, {type(right).__name__})"
        )


class ProperInEvaluator(IntervalOperationEvaluator):
    """
    Returns true if a point is properly in an interval.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.proper_in(left, right)

    @staticmethod
    def proper_in(point: Any, interval: Any) -> Optional[bool]:
        """Check if point is properly in interval."""
        if point is None or interval is None:
            return None

        in_interval = InEvaluator.in_interval(point, interval)
        if in_interval is None or not in_interval:
            return in_interval

        # A point is properly in an interval if it's strictly inside
        # (not on a closed boundary or on an open boundary)
        if isinstance(interval, Interval):
            start = interval.get_start()
            end = interval.get_end()

            # If point equals start or end, check closedness
            if point == start:
                return not interval.get_low_closed()
            if point == end:
                return not interval.get_high_closed()

            return True

        return False


class ProperIncludesEvaluator(IntervalOperationEvaluator):
    """
    Returns true if the first interval properly includes the second interval.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return ProperContainsEvaluator.proper_contains(left, right, context)


class ProperIncludedInEvaluator(IntervalOperationEvaluator):
    """
    Returns true if the first interval is properly included in the second interval.
    """

    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return ProperContainsEvaluator.proper_contains(right, left, context)


class BeforeEvaluator(IntervalOperationEvaluator):
    """
    Interval overload: returns true if first interval ends before second starts.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)

        # Import here to avoid circular imports
        from cql_engine.elm.evaluators.temporal import BeforeEvaluator as TemporalBefore
        return TemporalBefore.before(left, right, self.precision_str, context)


class AfterEvaluator(IntervalOperationEvaluator):
    """
    Interval overload: returns true if first interval starts after second ends.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)

        # Import here to avoid circular imports
        from cql_engine.elm.evaluators.temporal import AfterEvaluator as TemporalAfter
        return TemporalAfter.after(left, right, self.precision_str, context)


class MeetsEvaluator(IntervalOperationEvaluator):
    """
    Returns true if intervals meet (end-to-start or start-to-end).
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.meets(left, right, self.precision_str, context)

    @staticmethod
    def meets(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Check if intervals meet."""
        if left is None or right is None:
            return None

        if not (isinstance(left, Interval) and isinstance(right, Interval)):
            raise InvalidOperatorArgument(
                "meets(Interval<T>, Interval<T>)",
                f"meets({type(left).__name__}, {type(right).__name__})"
            )

        # Intervals meet if end of left equals start of right or vice versa
        left_end = left.get_end()
        right_start = right.get_start()
        right_end = right.get_end()
        left_start = left.get_start()

        # Check both directions
        return (left_end == right_start) or (right_end == left_start)


class MeetsBeforeEvaluator(IntervalOperationEvaluator):
    """
    Returns true if first interval meets second interval before it.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.meets_before(left, right, self.precision_str, context)

    @staticmethod
    def meets_before(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Check if left meets right before."""
        if left is None or right is None:
            return None

        if not (isinstance(left, Interval) and isinstance(right, Interval)):
            raise InvalidOperatorArgument(
                "meets_before(Interval<T>, Interval<T>)",
                f"meets_before({type(left).__name__}, {type(right).__name__})"
            )

        # Left meets right before if end of left equals start of right
        return left.get_end() == right.get_start()


class MeetsAfterEvaluator(IntervalOperationEvaluator):
    """
    Returns true if first interval meets second interval after it.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.meets_after(left, right, self.precision_str, context)

    @staticmethod
    def meets_after(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Check if left meets right after."""
        if left is None or right is None:
            return None

        if not (isinstance(left, Interval) and isinstance(right, Interval)):
            raise InvalidOperatorArgument(
                "meets_after(Interval<T>, Interval<T>)",
                f"meets_after({type(left).__name__}, {type(right).__name__})"
            )

        # Left meets right after if start of left equals end of right
        return left.get_start() == right.get_end()


class OverlapsEvaluator(IntervalOperationEvaluator):
    """
    Returns true if two intervals overlap.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.overlaps(left, right, self.precision_str, context)

    @staticmethod
    def overlaps(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Check if intervals overlap."""
        if left is None or right is None:
            return None

        if not (isinstance(left, Interval) and isinstance(right, Interval)):
            raise InvalidOperatorArgument(
                "overlaps(Interval<T>, Interval<T>)",
                f"overlaps({type(left).__name__}, {type(right).__name__})"
            )

        # Intervals overlap if they have a common point
        left_start = left.get_start()
        left_end = left.get_end()
        right_start = right.get_start()
        right_end = right.get_end()

        # Check if there's no gap between them
        return not (left_end < right_start or right_end < left_start)


class OverlapsBeforeEvaluator(IntervalOperationEvaluator):
    """
    Returns true if first interval overlaps before second interval.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.overlaps_before(left, right, self.precision_str, context)

    @staticmethod
    def overlaps_before(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Check if left overlaps before right."""
        if left is None or right is None:
            return None

        if not (isinstance(left, Interval) and isinstance(right, Interval)):
            raise InvalidOperatorArgument(
                "overlaps_before(Interval<T>, Interval<T>)",
                f"overlaps_before({type(left).__name__}, {type(right).__name__})"
            )

        # Left overlaps before right if it starts before and ends before right ends
        return (left.get_start() < right.get_start() and
                left.get_end() >= right.get_start() and
                left.get_end() < right.get_end())


class OverlapsAfterEvaluator(IntervalOperationEvaluator):
    """
    Returns true if first interval overlaps after second interval.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.overlaps_after(left, right, self.precision_str, context)

    @staticmethod
    def overlaps_after(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Check if left overlaps after right."""
        if left is None or right is None:
            return None

        if not (isinstance(left, Interval) and isinstance(right, Interval)):
            raise InvalidOperatorArgument(
                "overlaps_after(Interval<T>, Interval<T>)",
                f"overlaps_after({type(left).__name__}, {type(right).__name__})"
            )

        # Left overlaps after right if it starts after and starts before right ends
        return (left.get_start() > right.get_start() and
                left.get_start() <= right.get_end() and
                left.get_end() > right.get_end())


class CollapseEvaluator(IntervalOperationEvaluator):
    """
    Returns a list of non-overlapping intervals by merging overlapping intervals.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[List[Interval]]:
        operand = self.operand_expr.evaluate(context)
        return self.collapse(operand)

    @staticmethod
    def collapse(operand: Any) -> Optional[List[Interval]]:
        """Collapse overlapping intervals."""
        if operand is None:
            return None

        if not isinstance(operand, list):
            raise InvalidOperatorArgument(
                "collapse(List<Interval<T>>)",
                f"collapse({type(operand).__name__})"
            )

        if not operand:
            return []

        # Sort intervals by start point
        sorted_intervals = sorted(operand, key=lambda i: (i.get_start(), i.get_end()))

        result = []
        current = sorted_intervals[0]

        for interval in sorted_intervals[1:]:
            if _intervals_overlap_or_adjacent(current, interval):
                # Merge intervals
                current = Interval(
                    current.get_start(),
                    current.get_low_closed(),
                    max(current.get_end(), interval.get_end()),
                    current.get_high_closed() if current.get_end() > interval.get_end() else interval.get_high_closed()
                )
            else:
                result.append(current)
                current = interval

        result.append(current)
        return result


class ExpandEvaluator(IntervalOperationEvaluator):
    """
    Expands an interval by adding to both ends.
    """

    def __init__(self, operand_expr, expansion_expr):
        self.operand_expr = operand_expr
        self.expansion_expr = expansion_expr

    def evaluate(self, context: Context) -> Optional[Interval]:
        operand = self.operand_expr.evaluate(context)
        expansion = self.expansion_expr.evaluate(context)
        return self.expand(operand, expansion)

    @staticmethod
    def expand(operand: Any, expansion: Any) -> Optional[Interval]:
        """Expand interval."""
        if operand is None or expansion is None:
            return None

        if not isinstance(operand, Interval):
            raise InvalidOperatorArgument(
                "expand(Interval<T>, Quantity)",
                f"expand({type(operand).__name__}, {type(expansion).__name__})"
            )

        start = operand.get_start()
        end = operand.get_end()

        # Subtract expansion from start, add to end
        new_start = start - expansion if isinstance(start, (int, float, Decimal)) else start
        new_end = end + expansion if isinstance(end, (int, float, Decimal)) else end

        return Interval(new_start, operand.get_low_closed(), new_end, operand.get_high_closed())


class WidthEvaluator(IntervalOperationEvaluator):
    """
    Returns the width (size) of an interval.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return self.width(operand)

    @staticmethod
    def width(operand: Any) -> Optional[Decimal]:
        """Get width of interval."""
        if operand is None:
            return None

        if not isinstance(operand, Interval):
            raise InvalidOperatorArgument(
                "width(Interval<T>)",
                f"width({type(operand).__name__})"
            )

        start = operand.get_start()
        end = operand.get_end()

        if start is None or end is None:
            return None

        return Decimal(end - start)


class SizeEvaluator(IntervalOperationEvaluator):
    """
    Returns the size (width) of an interval.
    Alias for width in some contexts.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return WidthEvaluator.width(operand)


class PointFromEvaluator(IntervalOperationEvaluator):
    """
    Converts a single-point interval to a point value.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Any:
        operand = self.operand_expr.evaluate(context)
        return self.point_from(operand)

    @staticmethod
    def point_from(operand: Any) -> Any:
        """Extract point from single-point interval."""
        if operand is None:
            return None

        if not isinstance(operand, Interval):
            raise InvalidOperatorArgument(
                "point_from(Interval<T>)",
                f"point_from({type(operand).__name__})"
            )

        start = operand.get_start()
        end = operand.get_end()

        if start == end:
            return start

        return None


# Helper functions

def _compare_points(left: Any, right: Any, is_closed: bool) -> bool:
    """Compare two points with closure consideration."""
    if left is None or right is None:
        return left is None

    if is_closed:
        return left <= right
    else:
        return left < right


def _point_in_interval(point: Any, interval: Interval) -> Optional[bool]:
    """Check if a point is in an interval."""
    if point is None or interval is None:
        return None

    start = interval.get_start()
    end = interval.get_end()
    low_closed = interval.get_low_closed()
    high_closed = interval.get_high_closed()

    if start is not None:
        if low_closed:
            if point < start:
                return False
        else:
            if point <= start:
                return False

    if end is not None:
        if high_closed:
            if point > end:
                return False
        else:
            if point >= end:
                return False

    return True


def _intervals_overlap_or_adjacent(interval1: Interval, interval2: Interval) -> bool:
    """Check if two intervals overlap or are adjacent."""
    end1 = interval1.get_end()
    start2 = interval2.get_start()

    if end1 is None or start2 is None:
        return True

    if end1 < start2:
        return False

    if end1 == start2:
        # Adjacent if at least one boundary is closed
        return interval1.get_high_closed() or interval2.get_low_closed()

    return True
