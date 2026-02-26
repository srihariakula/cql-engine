"""
Comparison evaluators for CQL ELM execution engine.

This module contains evaluators for comparison operations including:
- Equality: Equal, NotEqual, Equivalent
- Ordering: Less, LessOrEqual, Greater, GreaterOrEqual
- Range: Between
- Temporal: SameAs, SameOrBefore, SameOrAfter
"""

from abc import ABC
from decimal import Decimal, ROUND_FLOOR
from typing import Any, Optional

from cql_engine.runtime.quantity import Quantity
from cql_engine.runtime.interval import Interval
from cql_engine.runtime.temporal import BaseTemporal
from cql_engine.runtime.cql_list import CqlList
from cql_engine.runtime.cql_type import CqlType
from cql_engine.runtime.value import Value
from cql_engine.exception import InvalidOperatorArgument


class Evaluator(ABC):
    """Base class for all evaluators."""

    def evaluate(self, context: Any) -> Any:
        """Evaluate the expression in the given context."""
        raise NotImplementedError


class EqualEvaluator(Evaluator):
    """
    Equal operator evaluator.

    Supports:
    - Equal(Boolean, Boolean) -> Boolean
    - Equal(Integer, Integer) -> Boolean
    - Equal(Long, Long) -> Boolean
    - Equal(Decimal, Decimal) -> Boolean
    - Equal(String, String) -> Boolean
    - Equal(Code, Code) -> Boolean
    - Equal(Concept, Concept) -> Boolean
    - Equal(Interval<T>, Interval<T>) -> Boolean
    - Equal(List<T>, List<T>) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._equal(left, right, context)

    @staticmethod
    def _equal(left: Any, right: Any, context: Optional[Any] = None) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, Interval) and isinstance(right, int):
            return left.equal(right)

        if isinstance(right, Interval) and isinstance(left, int):
            return right.equal(left)

        if type(left) != type(right):
            return False

        if isinstance(left, (bool, int, str)):
            return left == right

        if isinstance(left, Decimal):
            return left == right

        if isinstance(left, (list, tuple)):
            return CqlList.equal(left, right, context)

        if isinstance(left, CqlType):
            return left.equal(right)

        if context is not None:
            return context.object_equal(left, right)

        raise InvalidOperatorArgument(
            f"Equal({type(left).__name__}, {type(right).__name__}) requires Context and context was null",
            f"Equal({type(left).__name__}, {type(right).__name__})"
        )


class NotEqualEvaluator(Evaluator):
    """
    Not equal operator evaluator.

    Supports:
    - NotEqual(Boolean, Boolean) -> Boolean
    - NotEqual(Integer, Integer) -> Boolean
    - NotEqual(Decimal, Decimal) -> Boolean
    - NotEqual(String, String) -> Boolean
    - NotEqual(Interval<T>, Interval<T>) -> Boolean
    - NotEqual(List<T>, List<T>) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._not_equal(left, right, context)

    @staticmethod
    def _not_equal(left: Any, right: Any, context: Optional[Any] = None) -> Optional[bool]:
        result = EqualEvaluator._equal(left, right, context)
        return None if result is None else not result


class EquivalentEvaluator(Evaluator):
    """
    Equivalent operator evaluator.

    The ~ operator tests for equivalence, not strict equality.
    For decimals, equivalence means values are the same with comparison done
    on values rounded to the precision of the least precise operand.

    Supports:
    - Equivalent(Boolean, Boolean) -> Boolean
    - Equivalent(Integer, Integer) -> Boolean
    - Equivalent(Decimal, Decimal) -> Boolean
    - Equivalent(String, String) -> Boolean
    - Equivalent(Code, Code) -> Boolean
    - Equivalent(Concept, Concept) -> Boolean
    - Equivalent(Interval<T>, Interval<T>) -> Boolean
    - Equivalent(List<T>, List<T>) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._equivalent(left, right, context)

    @staticmethod
    def _equivalent(left: Any, right: Any, context: Optional[Any] = None) -> bool:
        if left is None and right is None:
            return True

        if left is None or right is None:
            return False

        if isinstance(left, Interval) and isinstance(right, int):
            return left.equivalent(right)

        if isinstance(right, Interval) and isinstance(left, int):
            return right.equivalent(left)

        if type(left) != type(right):
            return False

        if isinstance(left, (bool, int)):
            return left == right

        if isinstance(left, Decimal):
            left_decimal = Value.verify_precision(left, 0)
            right_decimal = Value.verify_precision(right, 0)
            min_scale = min(left_decimal.as_tuple().exponent, right_decimal.as_tuple().exponent)
            if min_scale >= 0:
                return (left_decimal.quantize(Decimal(10) ** -min_scale, rounding=ROUND_FLOOR) ==
                        right_decimal.quantize(Decimal(10) ** -min_scale, rounding=ROUND_FLOOR))
            return left_decimal == right_decimal

        if isinstance(left, (list, tuple)):
            return CqlList.equivalent(left, right, context)

        if isinstance(left, CqlType):
            return left.equivalent(right)

        if isinstance(left, str):
            return left.lower() == right.lower()

        if context is not None:
            return context.object_equivalent(left, right)

        raise InvalidOperatorArgument(
            f"Equivalent({type(left).__name__}, {type(right).__name__}) requires Context",
            f"Equivalent({type(left).__name__}, {type(right).__name__})"
        )


class LessEvaluator(Evaluator):
    """
    Less than operator evaluator.

    Supports:
    - Less(Integer, Integer) -> Boolean
    - Less(Long, Long) -> Boolean
    - Less(Decimal, Decimal) -> Boolean
    - Less(Quantity, Quantity) -> Boolean
    - Less(Date, Date) -> Boolean
    - Less(DateTime, DateTime) -> Boolean
    - Less(Time, Time) -> Boolean
    - Less(String, String) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._less(left, right, context)

    @staticmethod
    def _less(left: Any, right: Any, context: Optional[Any] = None) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            return left < right

        if isinstance(left, Decimal):
            return left < right

        if isinstance(left, Quantity):
            if left.value is None or right.value is None:
                return None
            compare_result = left.nullable_compare_to(right)
            return None if compare_result is None else compare_result < 0

        if isinstance(left, BaseTemporal):
            compare_result = left.compare(right, False)
            return None if compare_result is None else compare_result < 0

        if isinstance(left, str):
            return left < right

        if isinstance(left, Interval) and isinstance(right, int):
            # Check if right is in the interval
            if context and hasattr(context, 'in_interval'):
                if context.in_interval(right, left):
                    return None
            return left.end < right

        if isinstance(left, int) and isinstance(right, Interval):
            if context and hasattr(context, 'in_interval'):
                if context.in_interval(left, right):
                    return None
            return left < right.start

        raise InvalidOperatorArgument(
            "Less(Integer, Integer), Less(Decimal, Decimal), Less(Quantity, Quantity), "
            "Less(Date, Date), Less(DateTime, DateTime), Less(Time, Time), Less(String, String)",
            f"Less({type(left).__name__}, {type(right).__name__})"
        )


class LessOrEqualEvaluator(Evaluator):
    """
    Less than or equal operator evaluator.

    Supports:
    - LessOrEqual(Integer, Integer) -> Boolean
    - LessOrEqual(Long, Long) -> Boolean
    - LessOrEqual(Decimal, Decimal) -> Boolean
    - LessOrEqual(Quantity, Quantity) -> Boolean
    - LessOrEqual(Date, Date) -> Boolean
    - LessOrEqual(DateTime, DateTime) -> Boolean
    - LessOrEqual(Time, Time) -> Boolean
    - LessOrEqual(String, String) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._less_or_equal(left, right, context)

    @staticmethod
    def _less_or_equal(left: Any, right: Any, context: Optional[Any] = None) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            return left <= right

        if isinstance(left, Decimal):
            return left <= right

        if isinstance(left, Quantity):
            if left.value is None or right.value is None:
                return None
            compare_result = left.nullable_compare_to(right)
            return None if compare_result is None else compare_result <= 0

        if isinstance(left, BaseTemporal):
            compare_result = left.compare(right, False)
            return None if compare_result is None else compare_result <= 0

        if isinstance(left, str):
            return left <= right

        raise InvalidOperatorArgument(
            "LessOrEqual(Integer, Integer), LessOrEqual(Decimal, Decimal), LessOrEqual(Quantity, Quantity)",
            f"LessOrEqual({type(left).__name__}, {type(right).__name__})"
        )


class GreaterEvaluator(Evaluator):
    """
    Greater than operator evaluator.

    Supports:
    - Greater(Integer, Integer) -> Boolean
    - Greater(Long, Long) -> Boolean
    - Greater(Decimal, Decimal) -> Boolean
    - Greater(Quantity, Quantity) -> Boolean
    - Greater(Date, Date) -> Boolean
    - Greater(DateTime, DateTime) -> Boolean
    - Greater(Time, Time) -> Boolean
    - Greater(String, String) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._greater(left, right, context)

    @staticmethod
    def _greater(left: Any, right: Any, context: Optional[Any] = None) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            return left > right

        if isinstance(left, Decimal):
            return left > right

        if isinstance(left, Quantity):
            if left.value is None or right.value is None:
                return None
            compare_result = left.nullable_compare_to(right)
            return None if compare_result is None else compare_result > 0

        if isinstance(left, BaseTemporal):
            compare_result = left.compare(right, False)
            return None if compare_result is None else compare_result > 0

        if isinstance(left, str):
            return left > right

        if isinstance(left, Interval) and isinstance(right, int):
            if context and hasattr(context, 'in_interval'):
                if context.in_interval(right, left):
                    return None
            return left.start > right

        if isinstance(left, int) and isinstance(right, Interval):
            if context and hasattr(context, 'in_interval'):
                if context.in_interval(left, right):
                    return None
            return left > right.end

        raise InvalidOperatorArgument(
            "Greater(Integer, Integer), Greater(Decimal, Decimal), Greater(Quantity, Quantity)",
            f"Greater({type(left).__name__}, {type(right).__name__})"
        )


class GreaterOrEqualEvaluator(Evaluator):
    """
    Greater than or equal operator evaluator.

    Supports:
    - GreaterOrEqual(Integer, Integer) -> Boolean
    - GreaterOrEqual(Long, Long) -> Boolean
    - GreaterOrEqual(Decimal, Decimal) -> Boolean
    - GreaterOrEqual(Quantity, Quantity) -> Boolean
    - GreaterOrEqual(Date, Date) -> Boolean
    - GreaterOrEqual(DateTime, DateTime) -> Boolean
    - GreaterOrEqual(Time, Time) -> Boolean
    - GreaterOrEqual(String, String) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._greater_or_equal(left, right, context)

    @staticmethod
    def _greater_or_equal(left: Any, right: Any, context: Optional[Any] = None) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            return left >= right

        if isinstance(left, Decimal):
            return left >= right

        if isinstance(left, Quantity):
            if left.value is None or right.value is None:
                return None
            compare_result = left.nullable_compare_to(right)
            return None if compare_result is None else compare_result >= 0

        if isinstance(left, BaseTemporal):
            compare_result = left.compare(right, False)
            return None if compare_result is None else compare_result >= 0

        if isinstance(left, str):
            return left >= right

        raise InvalidOperatorArgument(
            "GreaterOrEqual(Integer, Integer), GreaterOrEqual(Decimal, Decimal), GreaterOrEqual(Quantity, Quantity)",
            f"GreaterOrEqual({type(left).__name__}, {type(right).__name__})"
        )


class BetweenEvaluator(Evaluator):
    """
    Between operator evaluator.

    Tests whether a value is between two other values (inclusive).

    Supports:
    - Between(value, low, high) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        value = self.operands[0].evaluate(context)
        low = self.operands[1].evaluate(context)
        high = self.operands[2].evaluate(context)
        return self._between(value, low, high, context)

    @staticmethod
    def _between(value: Any, low: Any, high: Any, context: Optional[Any] = None) -> Optional[bool]:
        if value is None or low is None or high is None:
            return None

        greater_or_equal = GreaterOrEqualEvaluator._greater_or_equal(value, low, context)
        if greater_or_equal is False:
            return False

        less_or_equal = LessOrEqualEvaluator._less_or_equal(value, high, context)
        if less_or_equal is False:
            return False

        if greater_or_equal is None or less_or_equal is None:
            return None

        return True


class SameAsEvaluator(Evaluator):
    """
    Same as operator evaluator for temporal values.

    Tests whether two temporal values occur at the same time.

    Supports:
    - SameAs(Date, Date) -> Boolean
    - SameAs(DateTime, DateTime) -> Boolean
    - SameAs(Time, Time) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._same_as(left, right)

    @staticmethod
    def _same_as(left: Any, right: Any) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            compare_result = left.compare(right, True)
            return compare_result == 0 if compare_result is not None else None

        raise InvalidOperatorArgument(
            "SameAs(Date, Date), SameAs(DateTime, DateTime), SameAs(Time, Time)",
            f"SameAs({type(left).__name__}, {type(right).__name__})"
        )


class SameOrBeforeEvaluator(Evaluator):
    """
    Same or before operator evaluator for temporal values.

    Tests whether the first temporal value occurs at the same time or before the second.

    Supports:
    - SameOrBefore(Date, Date) -> Boolean
    - SameOrBefore(DateTime, DateTime) -> Boolean
    - SameOrBefore(Time, Time) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._same_or_before(left, right)

    @staticmethod
    def _same_or_before(left: Any, right: Any) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            compare_result = left.compare(right, True)
            return None if compare_result is None else compare_result <= 0

        raise InvalidOperatorArgument(
            "SameOrBefore(Date, Date), SameOrBefore(DateTime, DateTime), SameOrBefore(Time, Time)",
            f"SameOrBefore({type(left).__name__}, {type(right).__name__})"
        )


class SameOrAfterEvaluator(Evaluator):
    """
    Same or after operator evaluator for temporal values.

    Tests whether the first temporal value occurs at the same time or after the second.

    Supports:
    - SameOrAfter(Date, Date) -> Boolean
    - SameOrAfter(DateTime, DateTime) -> Boolean
    - SameOrAfter(Time, Time) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._same_or_after(left, right)

    @staticmethod
    def _same_or_after(left: Any, right: Any) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            compare_result = left.compare(right, True)
            return None if compare_result is None else compare_result >= 0

        raise InvalidOperatorArgument(
            "SameOrAfter(Date, Date), SameOrAfter(DateTime, DateTime), SameOrAfter(Time, Time)",
            f"SameOrAfter({type(left).__name__}, {type(right).__name__})"
        )
