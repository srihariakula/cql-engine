"""
Arithmetic evaluators for CQL ELM execution engine.

This module contains evaluators for arithmetic operations including:
- Addition, Subtraction, Multiplication, Division
- Modulo, Truncated Division, Negation
- Absolute value, Ceiling, Floor, Truncate, Round
- Power, Logarithmic operations, Exponential
- And boundary/precision operations
"""

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_UP, ROUND_DOWN, ROUND_FLOOR, ROUND_CEILING
from typing import Any, Optional
import math

from cql_engine.runtime.quantity import Quantity
from cql_engine.runtime.interval import Interval
from cql_engine.runtime.temporal import BaseTemporal, Date, DateTime, Time, Precision, TemporalHelper
from cql_engine.runtime.value import Value
from cql_engine.exception import InvalidOperatorArgument


class Evaluator(ABC):
    """Base class for all evaluators."""

    @abstractmethod
    def evaluate(self, context: Any) -> Any:
        """Evaluate the expression in the given context."""
        pass


class AddEvaluator(Evaluator):
    """
    Addition operator evaluator.

    Supports:
    - Add(Integer, Integer) -> Integer
    - Add(Long, Long) -> Long
    - Add(Decimal, Decimal) -> Decimal
    - Add(Quantity, Quantity) -> Quantity
    - Add(Date, Quantity) -> Date
    - Add(DateTime, Quantity) -> DateTime
    - Add(Time, Quantity) -> Time
    - Add(String, String) -> String (concatenation)
    - Add(Interval, Interval) -> Interval
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._add(left, right)

    @staticmethod
    def _add(left: Any, right: Any) -> Any:
        if left is None or right is None:
            return None

        if isinstance(left, int) and isinstance(right, int):
            return left + right

        if isinstance(left, Decimal) and isinstance(right, Decimal):
            result = left + right
            return Value.verify_precision(result, None)

        if isinstance(left, Quantity) and isinstance(right, Quantity):
            return Quantity(
                value=left.value + right.value,
                unit=left.unit
            )

        if isinstance(left, BaseTemporal) and isinstance(right, Quantity):
            value_to_add_precision = Precision.from_string(right.unit)
            precision = Precision.from_string(BaseTemporal.get_lowest_precision(left))
            value_to_add = int(right.value)

            if isinstance(left, (DateTime, Date)):
                if value_to_add_precision == Precision.WEEK:
                    value_to_add = TemporalHelper.weeks_to_days(value_to_add)
                    value_to_add_precision = Precision.DAY

            if precision.to_datetime_index() < value_to_add_precision.to_datetime_index():
                value_to_add = TemporalHelper.truncate_value_to_target_precision(
                    value_to_add, value_to_add_precision, precision
                )
                value_to_add_precision = precision

            if isinstance(left, DateTime):
                return DateTime(
                    left.datetime.plus(value_to_add, value_to_add_precision.to_chrono_unit()),
                    precision
                )
            elif isinstance(left, Date):
                return Date(
                    left.date.plus(value_to_add, value_to_add_precision.to_chrono_unit())
                ).set_precision(precision)
            else:
                return Time(
                    left.time.plus(value_to_add, value_to_add_precision.to_chrono_unit()),
                    precision
                )

        if isinstance(left, Interval) and isinstance(right, Interval):
            return Interval(
                start=AddEvaluator._add(left.start, right.start),
                start_inclusive=True,
                end=AddEvaluator._add(left.end, right.end),
                end_inclusive=True
            )

        if isinstance(left, str) and isinstance(right, str):
            return left + right

        raise InvalidOperatorArgument(
            "Add(Integer, Integer), Add(Decimal, Decimal), Add(Quantity, Quantity), "
            "Add(Date, Quantity), Add(DateTime, Quantity), Add(Time, Quantity), Add(String, String)",
            f"Add({type(left).__name__}, {type(right).__name__})"
        )


class SubtractEvaluator(Evaluator):
    """
    Subtraction operator evaluator.

    Supports:
    - Subtract(Integer, Integer) -> Integer
    - Subtract(Long, Long) -> Long
    - Subtract(Decimal, Decimal) -> Decimal
    - Subtract(Quantity, Quantity) -> Quantity
    - Subtract(Date, Quantity) -> Date
    - Subtract(DateTime, Quantity) -> DateTime
    - Subtract(Time, Quantity) -> Time
    - Subtract(Interval, Interval) -> Interval
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._subtract(left, right)

    @staticmethod
    def _subtract(left: Any, right: Any) -> Any:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            return left - right

        if isinstance(left, Decimal):
            return left - right

        if isinstance(left, Quantity):
            return Quantity(
                value=left.value - right.value,
                unit=left.unit
            )

        if isinstance(left, BaseTemporal) and isinstance(right, Quantity):
            value_to_subtract_precision = Precision.from_string(right.unit)
            precision = Precision.from_string(BaseTemporal.get_lowest_precision(left))
            value_to_subtract = int(right.value)

            if isinstance(left, (DateTime, Date)):
                if value_to_subtract_precision == Precision.WEEK:
                    value_to_subtract = TemporalHelper.weeks_to_days(value_to_subtract)
                    value_to_subtract_precision = Precision.DAY

            if precision.to_datetime_index() < value_to_subtract_precision.to_datetime_index():
                value_to_subtract = TemporalHelper.truncate_value_to_target_precision(
                    value_to_subtract, value_to_subtract_precision, precision
                )
                value_to_subtract_precision = precision

            if isinstance(left, DateTime):
                return DateTime(
                    left.datetime.minus(value_to_subtract, value_to_subtract_precision.to_chrono_unit()),
                    precision
                )
            elif isinstance(left, Date):
                return Date(
                    left.date.minus(value_to_subtract, value_to_subtract_precision.to_chrono_unit())
                ).set_precision(precision)
            else:
                return Time(
                    left.time.minus(value_to_subtract, value_to_subtract_precision.to_chrono_unit()),
                    precision
                )

        if isinstance(left, Interval) and isinstance(right, Interval):
            return Interval(
                start=SubtractEvaluator._subtract(left.start, right.start),
                start_inclusive=True,
                end=SubtractEvaluator._subtract(left.end, right.end),
                end_inclusive=True
            )

        raise InvalidOperatorArgument(
            "Subtract(Integer, Integer), Subtract(Decimal, Decimal), Subtract(Quantity, Quantity), "
            "Subtract(Date, Quantity), Subtract(DateTime, Quantity), Subtract(Time, Quantity)",
            f"Subtract({type(left).__name__}, {type(right).__name__})"
        )


class MultiplyEvaluator(Evaluator):
    """
    Multiplication operator evaluator.

    Supports:
    - Multiply(Integer, Integer) -> Integer
    - Multiply(Long, Long) -> Long
    - Multiply(Decimal, Decimal) -> Decimal
    - Multiply(Decimal, Quantity) -> Quantity
    - Multiply(Quantity, Decimal) -> Quantity
    - Multiply(Quantity, Quantity) -> Quantity
    - Multiply(Interval, Interval) -> Interval
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._multiply(left, right)

    @staticmethod
    def _multiply(left: Any, right: Any) -> Any:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            return left * right

        if isinstance(left, Decimal) and isinstance(right, Decimal):
            result = left * right
            return Value.verify_precision(result, None)

        if isinstance(left, Quantity) and isinstance(right, Quantity):
            unit = right.unit if left.unit == "1" else left.unit
            value = Value.verify_precision(left.value * right.value, None)
            return Quantity(value=value, unit=unit)

        if isinstance(left, Decimal) and isinstance(right, Quantity):
            value = Value.verify_precision(left * right.value, None)
            return Quantity(value=value, unit=right.unit)

        if isinstance(left, Quantity) and isinstance(right, Decimal):
            value = Value.verify_precision(left.value * right, None)
            return Quantity(value=value, unit=left.unit)

        if isinstance(left, Interval) and isinstance(right, Interval):
            return Interval(
                start=MultiplyEvaluator._multiply(left.start, right.start),
                start_inclusive=True,
                end=MultiplyEvaluator._multiply(left.end, right.end),
                end_inclusive=True
            )

        raise InvalidOperatorArgument(
            "Multiply(Integer, Integer), Multiply(Decimal, Decimal), Multiply(Decimal, Quantity), "
            "Multiply(Quantity, Decimal), Multiply(Quantity, Quantity)",
            f"Multiply({type(left).__name__}, {type(right).__name__})"
        )


class DivideEvaluator(Evaluator):
    """
    Division operator evaluator.

    Supports:
    - Divide(Decimal, Decimal) -> Decimal
    - Divide(Quantity, Decimal) -> Quantity
    - Divide(Quantity, Quantity) -> Quantity
    - Divide(Interval, Interval) -> Interval
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._divide(left, right, context)

    @staticmethod
    def _divide_helper(left: Decimal, right: Decimal, context: Any) -> Optional[Decimal]:
        from cql_engine.elm.evaluators.comparison import EqualEvaluator

        if EqualEvaluator._equal(right, Decimal("0.0"), context):
            return None

        try:
            result = left / right
            return Value.verify_precision(result, None)
        except:
            return left.quantize(Decimal('0.00000001'), rounding=ROUND_FLOOR)

    @staticmethod
    def _divide(left: Any, right: Any, context: Any) -> Any:
        if left is None or right is None:
            return None

        if isinstance(left, Decimal) and isinstance(right, Decimal):
            return DivideEvaluator._divide_helper(left, right, context)

        if isinstance(left, Quantity) and isinstance(right, Quantity):
            value = DivideEvaluator._divide_helper(left.value, right.value, context)
            return Quantity(value=Value.verify_precision(value, None), unit=left.unit)

        if isinstance(left, Quantity) and isinstance(right, Decimal):
            value = DivideEvaluator._divide_helper(left.value, right, context)
            return Quantity(value=Value.verify_precision(value, None), unit=left.unit)

        if isinstance(left, Interval) and isinstance(right, Interval):
            return Interval(
                start=DivideEvaluator._divide(left.start, right.start, context),
                start_inclusive=True,
                end=DivideEvaluator._divide(left.end, right.end, context),
                end_inclusive=True
            )

        raise InvalidOperatorArgument(
            "Divide(Decimal, Decimal), Divide(Quantity, Decimal), Divide(Quantity, Quantity)",
            f"Divide({type(left).__name__}, {type(right).__name__})"
        )


class ModuloEvaluator(Evaluator):
    """
    Modulo operator evaluator.

    Supports:
    - Modulo(Integer, Integer) -> Integer
    - Modulo(Long, Long) -> Long
    - Modulo(Decimal, Decimal) -> Decimal
    - Modulo(Quantity, Quantity) -> Quantity
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._modulo(left, right)

    @staticmethod
    def _modulo(left: Any, right: Any) -> Any:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            if right == 0:
                return None
            return left % right

        if isinstance(left, Decimal):
            if right == Decimal("0.0"):
                return None
            return (left % right).quantize(Decimal('0.00000001'), rounding=ROUND_FLOOR)

        if isinstance(left, Quantity):
            if right.value == Decimal("0.0"):
                return None
            value = (left.value % right.value).quantize(Decimal('0.00000001'), rounding=ROUND_FLOOR)
            return Quantity(value=value, unit=left.unit)

        raise InvalidOperatorArgument(
            "Modulo(Integer, Integer), Modulo(Decimal, Decimal), Modulo(Quantity, Quantity)",
            f"Modulo({type(left).__name__}, {type(right).__name__})"
        )


class TruncatedDivideEvaluator(Evaluator):
    """
    Truncated division operator evaluator (integer division).

    Supports:
    - TruncatedDivide(Integer, Integer) -> Integer
    - TruncatedDivide(Long, Long) -> Long
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._truncated_divide(left, right)

    @staticmethod
    def _truncated_divide(left: Any, right: Any) -> Any:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            if right == 0:
                return None
            return left // right

        raise InvalidOperatorArgument(
            "TruncatedDivide(Integer, Integer), TruncatedDivide(Long, Long)",
            f"TruncatedDivide({type(left).__name__}, {type(right).__name__})"
        )


class NegateEvaluator(Evaluator):
    """
    Negation operator evaluator.

    Supports:
    - Negate(Integer) -> Integer
    - Negate(Long) -> Long
    - Negate(Decimal) -> Decimal
    - Negate(Quantity) -> Quantity
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._negate(operand)

    @staticmethod
    def _negate(source: Any) -> Any:
        if source is None:
            return None

        if isinstance(source, int):
            return -source

        if isinstance(source, Decimal):
            return -source

        if isinstance(source, Quantity):
            return Quantity(value=-source.value, unit=source.unit)

        raise InvalidOperatorArgument(
            "Negate(Integer), Negate(Decimal), Negate(Quantity)",
            f"Negate({type(source).__name__})"
        )


class AbsEvaluator(Evaluator):
    """
    Absolute value operator evaluator.

    Supports:
    - Abs(Integer) -> Integer
    - Abs(Long) -> Long
    - Abs(Decimal) -> Decimal
    - Abs(Quantity) -> Quantity
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._abs(operand)

    @staticmethod
    def _abs(operand: Any) -> Any:
        if operand is None:
            return None

        if isinstance(operand, int):
            return abs(operand)

        if isinstance(operand, Decimal):
            return abs(operand)

        if isinstance(operand, Quantity):
            return Quantity(value=abs(operand.value), unit=operand.unit)

        raise InvalidOperatorArgument(
            "Abs(Integer), Abs(Decimal), Abs(Quantity)",
            f"Abs({type(operand).__name__})"
        )


class CeilingEvaluator(Evaluator):
    """
    Ceiling operator evaluator.

    Supports:
    - Ceiling(Decimal) -> Integer
    - Ceiling(Quantity) -> Integer
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._ceiling(operand)

    @staticmethod
    def _ceiling(operand: Any) -> Any:
        if operand is None:
            return None

        if isinstance(operand, Decimal):
            return int(math.ceil(float(operand)))

        if isinstance(operand, Quantity):
            return int(math.ceil(float(operand.value)))

        raise InvalidOperatorArgument(
            "Ceiling(Decimal), Ceiling(Quantity)",
            f"Ceiling({type(operand).__name__})"
        )


class FloorEvaluator(Evaluator):
    """
    Floor operator evaluator.

    Supports:
    - Floor(Decimal) -> Integer
    - Floor(Quantity) -> Integer
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._floor(operand)

    @staticmethod
    def _floor(operand: Any) -> Any:
        if operand is None:
            return None

        if isinstance(operand, Decimal):
            return int(math.floor(float(operand)))

        if isinstance(operand, Quantity):
            return int(math.floor(float(operand.value)))

        raise InvalidOperatorArgument(
            "Floor(Decimal), Floor(Quantity)",
            f"Floor({type(operand).__name__})"
        )


class TruncateEvaluator(Evaluator):
    """
    Truncate operator evaluator.

    Supports:
    - Truncate(Decimal) -> Integer
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._truncate(operand)

    @staticmethod
    def _truncate(operand: Any) -> Any:
        if operand is None:
            return None

        if isinstance(operand, Decimal):
            val = float(operand)
            if val < 0:
                return int(operand.quantize(Decimal('1'), rounding=ROUND_CEILING))
            else:
                return int(operand.quantize(Decimal('1'), rounding=ROUND_FLOOR))

        raise InvalidOperatorArgument(
            "Truncate(Decimal)",
            f"Truncate({type(operand).__name__})"
        )


class RoundEvaluator(Evaluator):
    """
    Round operator evaluator.

    Supports:
    - Round(Decimal) -> Decimal
    - Round(Decimal, Integer) -> Decimal
    """

    def __init__(self, operand, precision=None):
        self.operand = operand
        self.precision = precision

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        precision = None if self.precision is None else self.precision.evaluate(context)
        return self._round(operand, precision)

    @staticmethod
    def _round(operand: Any, precision: Optional[int] = None) -> Any:
        if operand is None:
            return None

        if isinstance(operand, Decimal):
            rm = ROUND_UP if operand >= 0 else ROUND_DOWN

            if precision is None or precision == 0:
                return operand.quantize(Decimal('1'), rounding=rm)
            else:
                quantize_str = '0.' + '0' * precision
                return operand.quantize(Decimal(quantize_str), rounding=rm)

        raise InvalidOperatorArgument(
            "Round(Decimal) or Round(Decimal, Integer)",
            f"Round({type(operand).__name__})"
        )


class PowerEvaluator(Evaluator):
    """
    Power operator evaluator.

    Supports:
    - Power(Integer, Integer) -> Integer
    - Power(Long, Long) -> Long
    - Power(Decimal, Decimal) -> Decimal
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._power(left, right)

    @staticmethod
    def _power(left: Any, right: Any) -> Any:
        if left is None or right is None:
            return None

        if isinstance(left, int):
            if right < 0:
                return Decimal(1) / Decimal(left) ** abs(right)
            return Decimal(left) ** right

        if isinstance(left, Decimal):
            return Value.verify_precision(
                Decimal(str(math.pow(float(left), float(right)))), None
            )

        raise InvalidOperatorArgument(
            "Power(Integer, Integer), Power(Decimal, Decimal)",
            f"Power({type(left).__name__}, {type(right).__name__})"
        )


class LnEvaluator(Evaluator):
    """
    Natural logarithm operator evaluator.

    Supports:
    - Ln(Decimal) -> Decimal
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._ln(operand)

    @staticmethod
    def _ln(operand: Any) -> Any:
        if operand is None:
            return None

        if isinstance(operand, (int, Decimal)):
            value = float(operand)
            if value <= 0:
                return None
            return Decimal(str(math.log(value)))

        raise InvalidOperatorArgument(
            "Ln(Decimal)",
            f"Ln({type(operand).__name__})"
        )


class LogEvaluator(Evaluator):
    """
    Logarithm operator evaluator.

    Supports:
    - Log(Decimal, base Decimal) -> Decimal
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        operand = self.operands[0].evaluate(context)
        base = self.operands[1].evaluate(context)
        return self._log(operand, base)

    @staticmethod
    def _log(operand: Any, base: Any) -> Any:
        if operand is None or base is None:
            return None

        value = float(operand)
        base_value = float(base)

        if value <= 0 or base_value <= 0 or base_value == 1:
            return None

        return Decimal(str(math.log(value, base_value)))

        raise InvalidOperatorArgument(
            "Log(Decimal, Decimal)",
            f"Log({type(operand).__name__}, {type(base).__name__})"
        )


class ExpEvaluator(Evaluator):
    """
    Exponential operator evaluator.

    Supports:
    - Exp(Decimal) -> Decimal
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._exp(operand)

    @staticmethod
    def _exp(operand: Any) -> Any:
        if operand is None:
            return None

        if isinstance(operand, (int, Decimal)):
            return Decimal(str(math.exp(float(operand))))

        raise InvalidOperatorArgument(
            "Exp(Decimal)",
            f"Exp({type(operand).__name__})"
        )


class MinValueEvaluator(Evaluator):
    """
    Minimum value operator evaluator.

    Returns the minimum value for the given type.
    """

    def __init__(self, value_type: str):
        self.value_type = value_type

    def evaluate(self, context: Any) -> Any:
        return self._min_value(self.value_type)

    @staticmethod
    def _min_value(value_type: str) -> Any:
        type_map = {
            'Integer': -2147483648,
            'Long': -9223372036854775808,
            'Decimal': Decimal('-999999999.99999999'),
        }
        return type_map.get(value_type)


class MaxValueEvaluator(Evaluator):
    """
    Maximum value operator evaluator.

    Returns the maximum value for the given type.
    """

    def __init__(self, value_type: str):
        self.value_type = value_type

    def evaluate(self, context: Any) -> Any:
        return self._max_value(self.value_type)

    @staticmethod
    def _max_value(value_type: str) -> Any:
        type_map = {
            'Integer': 2147483647,
            'Long': 9223372036854775807,
            'Decimal': Decimal('999999999.99999999'),
        }
        return type_map.get(value_type)


class PredecessorEvaluator(Evaluator):
    """
    Predecessor operator evaluator.

    Returns the predecessor value (previous representable value).
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._predecessor(operand)

    @staticmethod
    def _predecessor(operand: Any) -> Any:
        if operand is None:
            return None

        if isinstance(operand, int):
            return operand - 1

        if isinstance(operand, Decimal):
            return operand - Decimal('0.00000001')

        raise InvalidOperatorArgument(
            "Predecessor(Integer), Predecessor(Decimal)",
            f"Predecessor({type(operand).__name__})"
        )


class SuccessorEvaluator(Evaluator):
    """
    Successor operator evaluator.

    Returns the successor value (next representable value).
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._successor(operand)

    @staticmethod
    def _successor(operand: Any) -> Any:
        if operand is None:
            return None

        if isinstance(operand, int):
            return operand + 1

        if isinstance(operand, Decimal):
            return operand + Decimal('0.00000001')

        raise InvalidOperatorArgument(
            "Successor(Integer), Successor(Decimal)",
            f"Successor({type(operand).__name__})"
        )


class PrecisionEvaluator(Evaluator):
    """
    Precision operator evaluator.

    Returns the precision of a value.
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._precision(operand)

    @staticmethod
    def _precision(operand: Any) -> Any:
        if operand is None:
            return None

        precision_map = {
            int: 'year',
            Decimal: 'year',
            Date: 'day',
            DateTime: 'second',
            Time: 'second',
        }

        for type_key, precision in precision_map.items():
            if isinstance(operand, type_key):
                return precision

        return None


class LowBoundaryEvaluator(Evaluator):
    """
    Low boundary operator evaluator.

    Returns the low boundary of an interval.
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._low_boundary(operand)

    @staticmethod
    def _low_boundary(operand: Any) -> Any:
        if isinstance(operand, Interval):
            return operand.start
        return operand


class HighBoundaryEvaluator(Evaluator):
    """
    High boundary operator evaluator.

    Returns the high boundary of an interval.
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._high_boundary(operand)

    @staticmethod
    def _high_boundary(operand: Any) -> Any:
        if isinstance(operand, Interval):
            return operand.end
        return operand
