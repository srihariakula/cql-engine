"""
Logical evaluators for CQL ELM execution engine.

This module contains evaluators for logical operations including:
- Boolean operations: And, Or, Not, Xor, Implies
- Null tests: IsNull, IsTrue, IsFalse
- Conditional: If, Case, Coalesce
- Special: Null
"""

from abc import ABC
from typing import Any, List, Optional

from cql_engine.exception import InvalidOperatorArgument


class Evaluator(ABC):
    """Base class for all evaluators."""

    def evaluate(self, context: Any) -> Any:
        """Evaluate the expression in the given context."""
        raise NotImplementedError


class AndEvaluator(Evaluator):
    """
    And operator evaluator.

    The and operator returns true if both its arguments are true.
    If either argument is false, the result is false. Otherwise, the result is null.

    Supports:
    - And(Boolean, Boolean) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._and(left, right)

    @staticmethod
    def _and(left: Any, right: Any) -> Optional[bool]:
        if left is None and right is None:
            return None

        if left is None and isinstance(right, bool):
            return None if right else False

        if right is None and isinstance(left, bool):
            return None if left else False

        if isinstance(left, bool) and isinstance(right, bool):
            return left and right

        raise InvalidOperatorArgument(
            "And(Boolean, Boolean)",
            f"And({type(left).__name__}, {type(right).__name__})"
        )


class OrEvaluator(Evaluator):
    """
    Or operator evaluator.

    The or operator returns true if either of its arguments are true.
    If both arguments are false, the result is false. Otherwise, the result is null.

    Supports:
    - Or(Boolean, Boolean) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._or(left, right)

    @staticmethod
    def _or(left: Any, right: Any) -> Optional[bool]:
        if left is None and right is None:
            return None

        if left is None and isinstance(right, bool):
            return True if right else None

        if right is None and isinstance(left, bool):
            return True if left else None

        if isinstance(left, bool) and isinstance(right, bool):
            return left or right

        raise InvalidOperatorArgument(
            "Or(Boolean, Boolean)",
            f"Or({type(left).__name__}, {type(right).__name__})"
        )


class NotEvaluator(Evaluator):
    """
    Not operator evaluator.

    The not operator returns true if the argument is false and false if the argument is true.
    Otherwise, the result is null.

    Supports:
    - Not(Boolean) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._not(operand)

    @staticmethod
    def _not(operand: Any) -> Optional[bool]:
        if operand is None:
            return None

        if isinstance(operand, bool):
            return not operand

        raise InvalidOperatorArgument(
            "Not(Boolean)",
            f"Not({type(operand).__name__})"
        )


class XorEvaluator(Evaluator):
    """
    Xor (exclusive or) operator evaluator.

    The xor operator returns true if one argument is true and the other is false.
    If both arguments are true or both arguments are false, the result is false.
    Otherwise, the result is null.

    Supports:
    - Xor(Boolean, Boolean) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._xor(left, right)

    @staticmethod
    def _xor(left: Any, right: Any) -> Optional[bool]:
        if left is None or right is None:
            return None

        if isinstance(left, bool) and isinstance(right, bool):
            return left ^ right

        raise InvalidOperatorArgument(
            "Xor(Boolean, Boolean)",
            f"Xor({type(left).__name__}, {type(right).__name__})"
        )


class ImpliesEvaluator(Evaluator):
    """
    Implies operator evaluator.

    The implies operator returns the logical implication of its arguments.
    If the left operand evaluates to true, this operator returns the boolean evaluation of the right operand.
    If the left operand evaluates to false, this operator returns true.
    Otherwise, this operator returns true if the right operand evaluates to true, and null otherwise.

    Truth table:
        | TRUE  FALSE  NULL
    --------------------------
    TRUE | TRUE  FALSE  NULL
    FALSE| TRUE  TRUE   TRUE
    NULL | TRUE  NULL   NULL

    Supports:
    - Implies(Boolean, Boolean) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._implies(left, right)

    @staticmethod
    def _implies(left: Optional[bool], right: Optional[bool]) -> Optional[bool]:
        if left is None:
            return None if (right is None or right is False) else True

        if left:
            return right

        return True


class IsNullEvaluator(Evaluator):
    """
    Is null operator evaluator.

    The is null operator determines whether or not its argument evaluates to null.
    If the argument evaluates to null, the result is true; otherwise, the result is false.

    Supports:
    - IsNull(Any) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._is_null(operand)

    @staticmethod
    def _is_null(operand: Any) -> bool:
        return operand is None


class IsTrueEvaluator(Evaluator):
    """
    Is true operator evaluator.

    The is true operator determines whether or not its argument evaluates to true.
    If the argument evaluates to true, the result is true; otherwise, the result is false.

    Supports:
    - IsTrue(Boolean) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._is_true(operand)

    @staticmethod
    def _is_true(operand: Optional[bool]) -> bool:
        return operand is True


class IsFalseEvaluator(Evaluator):
    """
    Is false operator evaluator.

    The is false operator determines whether or not its argument evaluates to false.
    If the argument evaluates to false, the result is true; otherwise, the result is false.

    Supports:
    - IsFalse(Boolean) -> Boolean
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._is_false(operand)

    @staticmethod
    def _is_false(operand: Optional[bool]) -> bool:
        return operand is False


class CoalesceEvaluator(Evaluator):
    """
    Coalesce operator evaluator.

    The Coalesce operator returns the first non-null result in a list of arguments.
    If all arguments evaluate to null, the result is null.
    The static type of the first argument determines the type of the result,
    and all subsequent arguments must be of that same type.

    Supports:
    - Coalesce<T>(argument1 T, argument2 T, ...) -> T
    - Coalesce<T>(arguments List<T>) -> T
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        evaluated_operands = [operand.evaluate(context) for operand in self.operands]
        return self._coalesce(evaluated_operands)

    @staticmethod
    def _coalesce(operands: List[Any]) -> Any:
        for operand in operands:
            if operand is not None:
                # Special case: if it's an iterable and there's only one operand
                if isinstance(operand, (list, tuple)) and len(operands) == 1:
                    for obj in operand:
                        if obj is not None:
                            return obj
                    return None
                return operand

        return None


class IfEvaluator(Evaluator):
    """
    If operator evaluator (ternary conditional).

    The if operator evaluates a condition and returns one of two expressions
    based on the result.

    Supports:
    - If(condition Boolean, then T, else T) -> T
    """

    def __init__(self, condition, then_clause, else_clause):
        self.condition = condition
        self.then_clause = then_clause
        self.else_clause = else_clause

    def evaluate(self, context: Any) -> Any:
        condition = self.condition.evaluate(context)

        # Null is treated as false
        if condition is None:
            condition = False

        return (self.then_clause.evaluate(context) if condition
                else self.else_clause.evaluate(context))


class CaseEvaluator(Evaluator):
    """
    Case operator evaluator.

    Supports both standard case (multiple when conditions) and selected case
    (comparing against a single comparand).

    Standard case:
        case
          when X > Y then X
          when Y > X then Y
          else 0
        end

    Selected case:
        case X
          when 1 then 12
          when 2 then 14
          else 15
        end

    Supports:
    - Case(comparand T, caseItems CaseItem[], else T) -> T
    - Case(caseItems CaseItem[], else T) -> T
    """

    def __init__(self, case_items: list, else_clause, comparand=None):
        self.case_items = case_items
        self.else_clause = else_clause
        self.comparand = comparand

    def evaluate(self, context: Any) -> Any:
        if self.comparand is None:
            return self._standard_case(context)
        else:
            return self._selected_case(context)

    def _standard_case(self, context: Any) -> Any:
        """Evaluates a standard case with boolean conditions."""
        for case_item in self.case_items:
            when_result = case_item['when'].evaluate(context)

            # Skip null conditions
            if when_result is None:
                continue

            if when_result:
                return case_item['then'].evaluate(context)

        return self.else_clause.evaluate(context)

    def _selected_case(self, context: Any) -> Any:
        """Evaluates a selected case comparing against a comparand."""
        comparand_value = self.comparand.evaluate(context)

        # Import here to avoid circular dependency
        from cql_engine.elm.evaluators.comparison import EquivalentEvaluator

        for case_item in self.case_items:
            when_result = case_item['when'].evaluate(context)
            check = EquivalentEvaluator._equivalent(comparand_value, when_result, context)

            if check is None:
                continue

            if check:
                return case_item['then'].evaluate(context)

        return self.else_clause.evaluate(context)


class NullEvaluator(Evaluator):
    """
    Null literal evaluator.

    Always returns null.

    Supports:
    - Null() -> Null
    """

    def evaluate(self, context: Any) -> Any:
        return None
