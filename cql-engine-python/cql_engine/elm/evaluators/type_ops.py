"""
Type operation evaluators for CQL ELM execution engine.

This module contains evaluators for type-related operations including:
- Type testing: Is
- Type casting: As
- Quantity conversion: ConvertQuantity, CanConvertQuantity
"""

from abc import ABC
from typing import Any, Optional

from cql_engine.exception import InvalidOperatorArgument


class Evaluator(ABC):
    """Base class for all evaluators."""

    def evaluate(self, context: Any) -> Any:
        """Evaluate the expression in the given context."""
        raise NotImplementedError


class IsEvaluator(Evaluator):
    """
    Is operator evaluator for type testing.

    The is operator allows the type of a result to be tested.
    If the run-time type of the argument is of the type being tested,
    the result of the operator is true; otherwise, the result is false.

    Supports:
    - Is<T>(argument Any) -> Boolean
    """

    def __init__(self, operand, is_type_specifier=None, is_type=None):
        self.operand = operand
        self.is_type_specifier = is_type_specifier
        self.is_type = is_type

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)

        # Resolve the type
        if self.is_type_specifier is not None:
            type_to_check = context.resolve_type(self.is_type_specifier)
        else:
            type_to_check = context.resolve_type(self.is_type)

        return context.is_type(operand, type_to_check)


class AsEvaluator(Evaluator):
    """
    As operator evaluator for type casting.

    The as operator allows the result of an expression to be cast as a given target type.
    This allows expressions to be written that are statically typed against the expected
    run-time type of the argument.
    If the argument is not of the specified type at run-time the result is null.

    The cast prefix indicates that if the argument is not of the specified type at
    run-time then an exception is thrown.

    Supports:
    - As<T>(argument Any) -> T
    - CastAs<T>(argument Any) -> T
    """

    def __init__(self, operand, as_type_specifier=None, as_type=None, is_strict=False):
        self.operand = operand
        self.as_type_specifier = as_type_specifier
        self.as_type = as_type
        self.is_strict = is_strict

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)

        # Resolve the type
        if self.as_type_specifier is not None:
            type_to_cast = context.resolve_type(self.as_type_specifier)
        else:
            type_to_cast = context.resolve_type(self.as_type)

        return context.cast_as(operand, type_to_cast, self.is_strict)


class CanConvertQuantityEvaluator(Evaluator):
    """
    CanConvertQuantity operator evaluator.

    The CanConvertQuantity operator returns true if a Quantity can be converted
    to a target unit. This is based on unit compatibility as defined by UCUM.

    Supports:
    - CanConvertQuantity(Quantity, targetUnit String) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        quantity = self.operands[0].evaluate(context)
        target_unit = self.operands[1].evaluate(context)
        return self._can_convert_quantity(quantity, target_unit, context)

    @staticmethod
    def _can_convert_quantity(quantity: Any, target_unit: Any, context: Optional[Any] = None) -> Optional[bool]:
        if quantity is None or target_unit is None:
            return None

        from cql_engine.runtime.quantity import Quantity

        if isinstance(quantity, Quantity) and isinstance(target_unit, str):
            # Check if UCUM service is available
            if context is None or not hasattr(context, 'ucum_service') or context.ucum_service is None:
                # If no UCUM service, we can't determine convertibility
                return False

            try:
                # Attempt a conversion to see if it's possible
                context.ucum_service.validate(target_unit)
                # Check if units are compatible
                # This is a simplified check - full implementation would use UCUM
                return quantity.unit == target_unit or _are_units_compatible(quantity.unit, target_unit)
            except:
                return False

        raise InvalidOperatorArgument(
            "CanConvertQuantity(Quantity, String)",
            f"CanConvertQuantity({type(quantity).__name__}, {type(target_unit).__name__})"
        )


class ConvertQuantityEvaluator(Evaluator):
    """
    ConvertQuantity operator evaluator.

    The ConvertQuantity operator converts a Quantity to an equivalent Quantity
    with the given unit. If the unit of the input quantity can be converted to
    the target unit, the result is an equivalent Quantity with the target unit.
    Otherwise, the result is null.

    Note that implementations are not required to support quantity conversion.
    Implementations that do support unit conversion shall do so according to
    the conversion specified by UCUM.

    Supports:
    - ConvertQuantity(Quantity, targetUnit String) -> Quantity
    - convert <quantity> to <unit>
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        quantity = self.operands[0].evaluate(context)
        target_unit = self.operands[1].evaluate(context)
        return self._convert_quantity(quantity, target_unit, context)

    @staticmethod
    def _convert_quantity(quantity: Any, target_unit: Any, context: Optional[Any] = None) -> Optional[Any]:
        if quantity is None or target_unit is None:
            return None

        from cql_engine.runtime.quantity import Quantity
        from decimal import Decimal

        if isinstance(quantity, Quantity) and isinstance(target_unit, str):
            # Check if UCUM service is available
            if context is None or not hasattr(context, 'ucum_service') or context.ucum_service is None:
                # Without UCUM service, can only handle same-unit conversions
                if quantity.unit == target_unit:
                    return Quantity(value=quantity.value, unit=target_unit)
                return None

            try:
                # Use UCUM service to convert
                # This is a simplified implementation
                ucum_service = context.ucum_service
                result = ucum_service.convert(quantity.value, quantity.unit, target_unit)

                if result is None:
                    return None

                # Convert result to Decimal
                if isinstance(result, (int, float)):
                    result_value = Decimal(str(result))
                else:
                    result_value = Decimal(result)

                return Quantity(value=result_value, unit=target_unit)
            except Exception:
                return None

        raise InvalidOperatorArgument(
            "ConvertQuantity(Quantity, String)",
            f"ConvertQuantity({type(quantity).__name__}, {type(target_unit).__name__})"
        )


def _are_units_compatible(unit1: str, unit2: str) -> bool:
    """
    Check if two units are compatible for conversion.
    This is a simplified implementation that handles common conversions.

    In a full implementation, this would use UCUM.
    """
    # Basic dimensional analysis
    unit_groups = {
        'length': {'m', 'cm', 'mm', 'km', 'ft', 'in', 'mi'},
        'mass': {'kg', 'g', 'mg', 'lb', 'oz'},
        'time': {'s', 'min', 'h', 'day', 'wk', 'mo', 'a'},
        'temperature': {'K', 'C', 'F'},
        'volume': {'L', 'mL', 'gal', 'pt', 'cup'},
    }

    for group in unit_groups.values():
        if unit1 in group and unit2 in group:
            return True

    return False
