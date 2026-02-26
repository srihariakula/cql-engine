"""
Type conversion evaluators for CQL ELM execution engine.

This module contains evaluators for type conversion operations including:
- Conversion functions: ToString, ToInteger, ToLong, ToDecimal, ToBoolean
- Temporal conversions: ToDate, ToDateTime, ToTime
- Complex conversions: ToQuantity, ToRatio, ToList, ToConc
ept
- Conversion checks: ConvertsToString, ConvertsToInteger, ConvertsToLong,
  ConvertsToDecimal, ConvertsToBoolean, ConvertsToDate, ConvertsToDateTime,
  ConvertsToTime, ConvertsToQuantity, ConvertsToRatio
- Generic: Convert
"""

from abc import ABC
from decimal import Decimal
from typing import Any, Optional

from cql_engine.exception import InvalidOperatorArgument


class Evaluator(ABC):
    """Base class for all evaluators."""

    def evaluate(self, context: Any) -> Any:
        """Evaluate the expression in the given context."""
        raise NotImplementedError


class ToStringEvaluator(Evaluator):
    """
    ToString operator evaluator.

    The ToString operator converts the value of its argument to a String value.

    Supports:
    - ToString(Boolean) -> String
    - ToString(Integer) -> String
    - ToString(Long) -> String
    - ToString(Decimal) -> String
    - ToString(Quantity) -> String
    - ToString(Ratio) -> String
    - ToString(Date) -> String
    - ToString(DateTime) -> String
    - ToString(Time) -> String
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_string(operand)

    @staticmethod
    def _to_string(operand: Any) -> Optional[str]:
        if operand is None:
            return None

        if isinstance(operand, str):
            return operand

        if isinstance(operand, (int, bool, Decimal)):
            return str(operand).lower() if isinstance(operand, bool) else str(operand)

        # For complex types (Quantity, Date, DateTime, Time, Ratio, etc.),
        # rely on their __str__ method
        return str(operand)


class ToIntegerEvaluator(Evaluator):
    """
    ToInteger operator evaluator.

    The ToInteger operator converts the value of its argument to an Integer value.
    The operator accepts strings using the format: (+|-)?#0

    Supports:
    - ToInteger(String) -> Integer
    - ToInteger(Boolean) -> Integer
    - ToInteger(Integer) -> Integer
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_integer(operand)

    @staticmethod
    def _to_integer(operand: Any) -> Optional[int]:
        if operand is None:
            return None

        if isinstance(operand, bool):
            return 1 if operand else 0

        if isinstance(operand, int):
            return operand

        if isinstance(operand, str):
            try:
                return int(operand)
            except ValueError:
                try:
                    float_val = float(operand)
                    # Validate that it's a valid integer value
                    if float_val == int(float_val):
                        return int(float_val)
                    return None
                except ValueError:
                    return None

        raise InvalidOperatorArgument(
            "ToInteger(String), ToInteger(Boolean), ToInteger(Integer)",
            f"ToInteger({type(operand).__name__})"
        )


class ToLongEvaluator(Evaluator):
    """
    ToLong operator evaluator.

    The ToLong operator converts the value of its argument to a Long value.
    The operator accepts strings using the format: (+|-)?#0

    Supports:
    - ToLong(String) -> Long
    - ToLong(Boolean) -> Long
    - ToLong(Integer) -> Long
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_long(operand)

    @staticmethod
    def _to_long(operand: Any) -> Optional[int]:
        if operand is None:
            return None

        if isinstance(operand, bool):
            return 1 if operand else 0

        if isinstance(operand, int):
            return operand

        if isinstance(operand, str):
            try:
                return int(operand)
            except ValueError:
                return None

        raise InvalidOperatorArgument(
            "ToLong(String), ToLong(Boolean), ToLong(Integer)",
            f"ToLong({type(operand).__name__})"
        )


class ToDecimalEvaluator(Evaluator):
    """
    ToDecimal operator evaluator.

    The ToDecimal operator converts the value of its argument to a Decimal value.
    The operator accepts strings using the format: (+|-)?#0(.0#)?

    Supports:
    - ToDecimal(String) -> Decimal
    - ToDecimal(Boolean) -> Decimal
    - ToDecimal(Integer) -> Decimal
    - ToDecimal(Long) -> Decimal
    - ToDecimal(Decimal) -> Decimal
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_decimal(operand)

    @staticmethod
    def _to_decimal(operand: Any) -> Optional[Decimal]:
        if operand is None:
            return None

        if isinstance(operand, bool):
            return Decimal("1.0") if operand else Decimal("0.0")

        if isinstance(operand, Decimal):
            return operand

        if isinstance(operand, int):
            return Decimal(operand)

        if isinstance(operand, str):
            try:
                if "." in operand:
                    decimal_split = operand.split(".")
                    # Invalid format checks
                    if (decimal_split[0] and
                        (decimal_split[0][-1] in "-+") and
                        len(decimal_split[0]) == 1):
                        return None
                    if not decimal_split[0] or not decimal_split[0].strip("+-"):
                        return None

                result = Decimal(operand)
                # Validate precision/scale
                return result
            except:
                return None

        raise InvalidOperatorArgument(
            "ToDecimal(String), ToDecimal(Boolean), ToDecimal(Integer), ToDecimal(Decimal)",
            f"ToDecimal({type(operand).__name__})"
        )


class ToBooleanEvaluator(Evaluator):
    """
    ToBoolean operator evaluator.

    The ToBoolean operator converts the value of its argument to a Boolean value.
    The operator accepts:
    - true: true t yes y 1
    - false: false f no n 0

    Supports:
    - ToBoolean(String) -> Boolean
    - ToBoolean(Boolean) -> Boolean
    - ToBoolean(Integer) -> Boolean
    - ToBoolean(Decimal) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_boolean(operand)

    @staticmethod
    def _to_boolean(operand: Any) -> Optional[bool]:
        if operand is None:
            return None

        if isinstance(operand, bool):
            return operand

        if isinstance(operand, int):
            if operand == 1:
                return True
            if operand == 0:
                return False
            return None

        if isinstance(operand, Decimal):
            if operand == Decimal("0.0") or operand == Decimal("0"):
                return False
            if operand == Decimal("1.0") or operand == Decimal("1"):
                return True
            return None

        if isinstance(operand, str):
            compare = operand.lower()
            if compare in ("true", "t", "yes", "y", "1"):
                return True
            if compare in ("false", "f", "no", "n", "0"):
                return False
            return None

        raise InvalidOperatorArgument(
            "ToBoolean(String), ToBoolean(Boolean), ToBoolean(Integer), ToBoolean(Decimal)",
            f"ToBoolean({type(operand).__name__})"
        )


class ToDateEvaluator(Evaluator):
    """
    ToDate operator evaluator.

    The ToDate operator converts the value of its argument to a Date value.

    Supports:
    - ToDate(String) -> Date
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_date(operand)

    @staticmethod
    def _to_date(operand: Any) -> Optional[Any]:
        if operand is None:
            return None

        # Import here to avoid circular dependency
        from cql_engine.runtime.temporal import Date

        if isinstance(operand, Date):
            return operand

        if isinstance(operand, str):
            try:
                return Date.parse(operand)
            except:
                return None

        raise InvalidOperatorArgument(
            "ToDate(String)",
            f"ToDate({type(operand).__name__})"
        )


class ToDateTimeEvaluator(Evaluator):
    """
    ToDateTime operator evaluator.

    The ToDateTime operator converts the value of its argument to a DateTime value.

    Supports:
    - ToDateTime(String) -> DateTime
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_datetime(operand)

    @staticmethod
    def _to_datetime(operand: Any) -> Optional[Any]:
        if operand is None:
            return None

        from cql_engine.runtime.temporal import DateTime

        if isinstance(operand, DateTime):
            return operand

        if isinstance(operand, str):
            try:
                return DateTime.parse(operand)
            except:
                return None

        raise InvalidOperatorArgument(
            "ToDateTime(String)",
            f"ToDateTime({type(operand).__name__})"
        )


class ToTimeEvaluator(Evaluator):
    """
    ToTime operator evaluator.

    The ToTime operator converts the value of its argument to a Time value.

    Supports:
    - ToTime(String) -> Time
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_time(operand)

    @staticmethod
    def _to_time(operand: Any) -> Optional[Any]:
        if operand is None:
            return None

        from cql_engine.runtime.temporal import Time

        if isinstance(operand, Time):
            return operand

        if isinstance(operand, str):
            try:
                return Time.parse(operand)
            except:
                return None

        raise InvalidOperatorArgument(
            "ToTime(String)",
            f"ToTime({type(operand).__name__})"
        )


class ToQuantityEvaluator(Evaluator):
    """
    ToQuantity operator evaluator.

    The ToQuantity operator converts a value to a Quantity.

    Supports:
    - ToQuantity(Decimal) -> Quantity
    - ToQuantity(Integer) -> Quantity
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_quantity(operand)

    @staticmethod
    def _to_quantity(operand: Any) -> Optional[Any]:
        if operand is None:
            return None

        from cql_engine.runtime.quantity import Quantity

        if isinstance(operand, Quantity):
            return operand

        if isinstance(operand, (int, Decimal)):
            return Quantity(value=Decimal(str(operand)), unit="1")

        raise InvalidOperatorArgument(
            "ToQuantity(Decimal), ToQuantity(Integer)",
            f"ToQuantity({type(operand).__name__})"
        )


class ToRatioEvaluator(Evaluator):
    """
    ToRatio operator evaluator.

    The ToRatio operator converts values to a Ratio.

    Supports:
    - ToRatio(Decimal, Decimal) -> Ratio
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        # Typically takes numerator and denominator
        if len(self.operands) >= 2:
            numerator = self.operands[0].evaluate(context)
            denominator = self.operands[1].evaluate(context)
            return self._to_ratio(numerator, denominator)
        else:
            operand = self.operands[0].evaluate(context)
            return self._to_ratio(operand)

    @staticmethod
    def _to_ratio(operand: Any, denominator: Any = None) -> Optional[Any]:
        if operand is None:
            return None

        from cql_engine.runtime.ratio import Ratio

        if isinstance(operand, Ratio):
            return operand

        # Create a ratio from numerator and denominator
        if denominator is not None:
            from cql_engine.runtime.quantity import Quantity
            num = Quantity(value=Decimal(str(operand)), unit="1")
            denom = Quantity(value=Decimal(str(denominator)), unit="1")
            return Ratio(numerator=num, denominator=denom)

        raise InvalidOperatorArgument(
            "ToRatio(Decimal, Decimal)",
            f"ToRatio({type(operand).__name__})"
        )


class ToConceptEvaluator(Evaluator):
    """
    ToConcept operator evaluator.

    The ToConcept operator converts a Code to a Concept.

    Supports:
    - ToConcept(Code) -> Concept
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_concept(operand)

    @staticmethod
    def _to_concept(operand: Any) -> Optional[Any]:
        if operand is None:
            return None

        # Import here to avoid circular dependency
        from cql_engine.runtime.code import Code, Concept

        if isinstance(operand, Concept):
            return operand

        if isinstance(operand, Code):
            return Concept(codes=[operand])

        raise InvalidOperatorArgument(
            "ToConcept(Code)",
            f"ToConcept({type(operand).__name__})"
        )


class ToListEvaluator(Evaluator):
    """
    ToList operator evaluator.

    The ToList operator converts a value to a list containing that value.

    Supports:
    - ToList<T>(element T) -> List<T>
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._to_list(operand)

    @staticmethod
    def _to_list(operand: Any) -> Optional[list]:
        if operand is None:
            return None

        if isinstance(operand, (list, tuple)):
            return list(operand)

        return [operand]


class ConvertEvaluator(Evaluator):
    """
    Convert operator evaluator.

    Generic conversion operator that converts to a specified type.

    Supports:
    - Convert(operand Any, type String) -> Any
    """

    def __init__(self, operand, to_type):
        self.operand = operand
        self.to_type = to_type

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        to_type = self.to_type.evaluate(context) if hasattr(self.to_type, 'evaluate') else self.to_type
        return self._convert(operand, to_type)

    @staticmethod
    def _convert(operand: Any, to_type: str) -> Optional[Any]:
        type_map = {
            "String": ToStringEvaluator._to_string,
            "Integer": ToIntegerEvaluator._to_integer,
            "Long": ToLongEvaluator._to_long,
            "Decimal": ToDecimalEvaluator._to_decimal,
            "Boolean": ToBooleanEvaluator._to_boolean,
            "Date": ToDateEvaluator._to_date,
            "DateTime": ToDateTimeEvaluator._to_datetime,
            "Time": ToTimeEvaluator._to_time,
            "Quantity": ToQuantityEvaluator._to_quantity,
        }

        converter = type_map.get(to_type)
        if converter:
            return converter(operand)

        return None


class ConvertsToStringEvaluator(Evaluator):
    """
    ConvertsToString operator evaluator.

    The ConvertsToString operator returns true if its argument is or can be
    converted to a String value.

    Supports:
    - ConvertsToString(Boolean) -> Boolean
    - ConvertsToString(Integer) -> Boolean
    - ConvertsToString(Long) -> Boolean
    - ConvertsToString(Decimal) -> Boolean
    - ConvertsToString(Quantity) -> Boolean
    - ConvertsToString(Ratio) -> Boolean
    - ConvertsToString(Date) -> Boolean
    - ConvertsToString(DateTime) -> Boolean
    - ConvertsToString(Time) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_string(operand)

    @staticmethod
    def _converts_to_string(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        convertible_types = (
            bool, int, str, Decimal,
            # Will check for Quantity, Ratio, Date, DateTime, Time using duck typing
        )

        if isinstance(argument, convertible_types):
            return True

        # Check for complex types by class name
        type_name = type(argument).__name__
        if type_name in ("Quantity", "Ratio", "Date", "DateTime", "Time"):
            return True

        return False


class ConvertsToIntegerEvaluator(Evaluator):
    """
    ConvertsToInteger operator evaluator.

    The ConvertsToInteger operator returns true if its argument is or can be
    converted to an Integer value.

    Supports:
    - ConvertsToInteger(String) -> Boolean
    - ConvertsToInteger(Boolean) -> Boolean
    - ConvertsToInteger(Integer) -> Boolean
    - ConvertsToInteger(Long) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_integer(operand)

    @staticmethod
    def _converts_to_integer(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if isinstance(argument, (bool, int)):
            return True

        if isinstance(argument, str):
            try:
                int(argument)
                return True
            except ValueError:
                return False

        return False


class ConvertsToLongEvaluator(Evaluator):
    """
    ConvertsToLong operator evaluator.

    The ConvertsToLong operator returns true if its argument is or can be
    converted to a Long value.

    Supports:
    - ConvertsToLong(String) -> Boolean
    - ConvertsToLong(Boolean) -> Boolean
    - ConvertsToLong(Integer) -> Boolean
    - ConvertsToLong(Long) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_long(operand)

    @staticmethod
    def _converts_to_long(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if isinstance(argument, (bool, int)):
            return True

        if isinstance(argument, str):
            try:
                int(argument)
                return True
            except ValueError:
                return False

        return False


class ConvertsToDecimalEvaluator(Evaluator):
    """
    ConvertsToDecimal operator evaluator.

    The ConvertsToDecimal operator returns true if its argument is or can be
    converted to a Decimal value.

    Supports:
    - ConvertsToDecimal(String) -> Boolean
    - ConvertsToDecimal(Boolean) -> Boolean
    - ConvertsToDecimal(Integer) -> Boolean
    - ConvertsToDecimal(Long) -> Boolean
    - ConvertsToDecimal(Decimal) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_decimal(operand)

    @staticmethod
    def _converts_to_decimal(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if isinstance(argument, (bool, int, Decimal)):
            return True

        if isinstance(argument, str):
            try:
                Decimal(argument)
                return True
            except:
                return False

        return False


class ConvertsToBooleanEvaluator(Evaluator):
    """
    ConvertsToBoolean operator evaluator.

    The ConvertsToBoolean operator returns true if its argument is or can be
    converted to a Boolean value.

    Supports:
    - ConvertsToBoolean(String) -> Boolean
    - ConvertsToBoolean(Boolean) -> Boolean
    - ConvertsToBoolean(Integer) -> Boolean
    - ConvertsToBoolean(Decimal) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_boolean(operand)

    @staticmethod
    def _converts_to_boolean(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if isinstance(argument, bool):
            return True

        if isinstance(argument, int):
            return argument in (0, 1)

        if isinstance(argument, Decimal):
            return argument in (Decimal("0"), Decimal("0.0"), Decimal("1"), Decimal("1.0"))

        if isinstance(argument, str):
            compare = argument.lower()
            return compare in ("true", "t", "yes", "y", "1", "false", "f", "no", "n", "0")

        return False


class ConvertsToDateEvaluator(Evaluator):
    """
    ConvertsToDate operator evaluator.

    The ConvertsToDate operator returns true if its argument is or can be
    converted to a Date value.

    Supports:
    - ConvertsToDate(String) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_date(operand)

    @staticmethod
    def _converts_to_date(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if type(argument).__name__ == "Date":
            return True

        if isinstance(argument, str):
            try:
                from cql_engine.runtime.temporal import Date
                Date.parse(argument)
                return True
            except:
                return False

        return False


class ConvertsToDateTimeEvaluator(Evaluator):
    """
    ConvertsToDateTime operator evaluator.

    The ConvertsToDateTime operator returns true if its argument is or can be
    converted to a DateTime value.

    Supports:
    - ConvertsToDateTime(String) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_datetime(operand)

    @staticmethod
    def _converts_to_datetime(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if type(argument).__name__ == "DateTime":
            return True

        if isinstance(argument, str):
            try:
                from cql_engine.runtime.temporal import DateTime
                DateTime.parse(argument)
                return True
            except:
                return False

        return False


class ConvertsToTimeEvaluator(Evaluator):
    """
    ConvertsToTime operator evaluator.

    The ConvertsToTime operator returns true if its argument is or can be
    converted to a Time value.

    Supports:
    - ConvertsToTime(String) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_time(operand)

    @staticmethod
    def _converts_to_time(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if type(argument).__name__ == "Time":
            return True

        if isinstance(argument, str):
            try:
                from cql_engine.runtime.temporal import Time
                Time.parse(argument)
                return True
            except:
                return False

        return False


class ConvertsToQuantityEvaluator(Evaluator):
    """
    ConvertsToQuantity operator evaluator.

    The ConvertsToQuantity operator returns true if its argument is or can be
    converted to a Quantity value.

    Supports:
    - ConvertsToQuantity(Decimal) -> Boolean
    - ConvertsToQuantity(Integer) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_quantity(operand)

    @staticmethod
    def _converts_to_quantity(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if type(argument).__name__ == "Quantity":
            return True

        if isinstance(argument, (int, Decimal)):
            return True

        return False


class ConvertsToRatioEvaluator(Evaluator):
    """
    ConvertsToRatio operator evaluator.

    The ConvertsToRatio operator returns true if its argument is or can be
    converted to a Ratio value.

    Supports:
    - ConvertsToRatio(Quantity, Quantity) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._converts_to_ratio(operand)

    @staticmethod
    def _converts_to_ratio(argument: Any) -> Optional[bool]:
        if argument is None:
            return None

        if type(argument).__name__ == "Ratio":
            return True

        return False
