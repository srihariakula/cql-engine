"""
Definition and reference evaluators for CQL expressions.

Handles expression definitions, function definitions, parameter references, etc.
"""

from abc import ABC
from typing import Any, Optional, List, Dict
from decimal import Decimal

from cql_engine.execution.context import Context
from cql_engine.execution.exceptions import InvalidOperatorArgument
from cql_engine.runtime.tuple import Tuple
from cql_engine.runtime.cql_code import Code, Concept


class DefinitionEvaluator(ABC):
    """Base class for definition evaluators."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the definition."""
        raise NotImplementedError


class ExpressionDefEvaluator(DefinitionEvaluator):
    """
    Evaluates an expression definition.
    Supports caching and context management.
    """

    def __init__(self, name: str, expression, context_name: Optional[str] = None):
        self.name = name
        self.expression = expression
        self.context_name = context_name

    def evaluate(self, context: Context) -> Any:
        """Evaluate expression definition."""
        if self.context_name:
            context.enter_context(self.context_name)

        try:
            # Push evaluated resource stack for tracking
            context.push_evaluated_resource_stack()

            # Check cache if enabled
            if context.is_expression_caching_enabled():
                cached = context.get_cached_expression(self.name)
                if cached:
                    return cached

            # Evaluate expression
            value = self.expression.evaluate(context)

            # Cache if enabled
            if context.is_expression_caching_enabled():
                context.cache_expression(self.name, value)

            return value

        finally:
            context.pop_evaluated_resource_stack()
            if self.context_name:
                context.exit_context()


class FunctionDefEvaluator(DefinitionEvaluator):
    """
    Represents a function definition.
    Functions are called through FunctionRefEvaluator.
    """

    def __init__(self, name: str, operand_params: List[str], return_type: str, expression):
        self.name = name
        self.operand_params = operand_params
        self.return_type = return_type
        self.expression = expression

    def evaluate(self, context: Context, operands: List[Any]) -> Any:
        """Evaluate function with given operands."""
        if len(operands) != len(self.operand_params):
            raise InvalidOperatorArgument(
                f"{self.name}({', '.join(self.operand_params)})",
                f"{self.name}(...) - got {len(operands)} args, expected {len(self.operand_params)}"
            )

        # Push operand context
        for param_name, operand_value in zip(self.operand_params, operands):
            context.push_variable(param_name, operand_value)

        try:
            return self.expression.evaluate(context)
        finally:
            # Pop all operand variables
            for _ in self.operand_params:
                context.pop_variable()


class FunctionRefEvaluator(DefinitionEvaluator):
    """
    References and invokes a function.
    """

    def __init__(self, function_name: str, operands: List[Any], library_name: Optional[str] = None):
        self.function_name = function_name
        self.operands = operands
        self.library_name = library_name

    def evaluate(self, context: Context) -> Any:
        """Call the referenced function."""
        # Evaluate operands
        operand_values = [op.evaluate(context) for op in self.operands]

        # Resolve function
        func_def = context.resolve_function_ref(self.function_name, self.library_name)

        if func_def is None:
            raise InvalidOperatorArgument(
                f"Function {self.function_name} not found",
                f"FunctionRef({self.function_name})"
            )

        # Call function
        return func_def.evaluate(context, operand_values)


class ExpressionRefEvaluator(DefinitionEvaluator):
    """
    References an expression definition.
    """

    def __init__(self, expression_name: str, library_name: Optional[str] = None):
        self.expression_name = expression_name
        self.library_name = library_name

    def evaluate(self, context: Context) -> Any:
        """Resolve and evaluate the referenced expression."""
        return context.resolve_expression_ref(self.expression_name, self.library_name)


class OperandRefEvaluator(DefinitionEvaluator):
    """
    References an operand (parameter) in a function.
    """

    def __init__(self, operand_name: str):
        self.operand_name = operand_name

    def evaluate(self, context: Context) -> Any:
        """Get operand value."""
        return context.resolve_variable(self.operand_name).get_value()


class ParameterRefEvaluator(DefinitionEvaluator):
    """
    References a parameter in the context.
    """

    def __init__(self, parameter_name: str, library_name: Optional[str] = None):
        self.parameter_name = parameter_name
        self.library_name = library_name

    def evaluate(self, context: Context) -> Any:
        """Get parameter value."""
        return context.resolve_parameter_ref(self.library_name, self.parameter_name)


class ParameterDefEvaluator(DefinitionEvaluator):
    """
    Represents a parameter definition.
    """

    def __init__(self, name: str, param_type: str, default_value: Optional[Any] = None):
        self.name = name
        self.param_type = param_type
        self.default_value = default_value

    def evaluate(self, context: Context) -> Any:
        """Get parameter value (from context or default)."""
        value = context.get_parameter(self.name)
        if value is None:
            return self.default_value
        return value


class IdentifierRefEvaluator(DefinitionEvaluator):
    """
    References an identifier (global value) in the context.
    """

    def __init__(self, identifier_name: str):
        self.identifier_name = identifier_name

    def evaluate(self, context: Context) -> Any:
        """Resolve identifier reference."""
        return context.resolve_identifier_ref(self.identifier_name)


class PropertyEvaluator(DefinitionEvaluator):
    """
    Accesses a property of a value.
    """

    def __init__(self, path: str, source_expr=None, scope: Optional[str] = None):
        self.path = path
        self.source_expr = source_expr
        self.scope = scope

    def evaluate(self, context: Context) -> Any:
        """Get property value."""
        target = None

        if self.source_expr:
            target = self.source_expr.evaluate(context)

            # Tuple element access
            if isinstance(target, Tuple):
                return target.get_elements().get(self.path)

        elif self.scope:
            target = context.resolve_variable(self.scope, is_let=True).get_value()

        if target is None:
            return None

        # Handle iterable (property projection)
        if isinstance(target, (list, tuple)):
            return [context.resolve_path(item, self.path) for item in target]

        # Regular property access
        return context.resolve_path(target, self.path)


class TupleEvaluator(DefinitionEvaluator):
    """
    Constructs a tuple from named elements.
    """

    def __init__(self, elements: Dict[str, Any]):
        self.elements = elements  # Dict of {name: expression}

    def evaluate(self, context: Context) -> Tuple:
        """Construct tuple."""
        element_values = {}
        for name, expr in self.elements.items():
            element_values[name] = expr.evaluate(context)

        return Tuple(context).with_elements(element_values)


class TupleElementEvaluator(DefinitionEvaluator):
    """
    Represents an element in a tuple definition.
    """

    def __init__(self, name: str, value_expr):
        self.name = name
        self.value_expr = value_expr

    def evaluate(self, context: Context) -> tuple:
        """Return (name, value) pair."""
        return (self.name, self.value_expr.evaluate(context))


class InstanceEvaluator(DefinitionEvaluator):
    """
    Creates an instance of a type.
    """

    def __init__(self, class_type: str, elements: Dict[str, Any]):
        self.class_type = class_type
        self.elements = elements  # Dict of {name: expression}

    def evaluate(self, context: Context) -> Any:
        """Create instance."""
        element_values = {}
        for name, expr in self.elements.items():
            element_values[name] = expr.evaluate(context)

        # TODO: Instantiate actual class type
        return Tuple(context).with_elements(element_values)


class LiteralEvaluator(DefinitionEvaluator):
    """
    Evaluates a literal value.
    """

    def __init__(self, value: str, value_type: str):
        self.value = value
        self.value_type = value_type.lower()

    def evaluate(self, context: Context) -> Any:
        """Parse and return literal value."""
        try:
            if self.value_type == 'boolean':
                return self.value.lower() in ('true', '1', 'yes')
            elif self.value_type == 'integer':
                return int(self.value)
            elif self.value_type == 'long':
                return int(self.value)
            elif self.value_type == 'decimal':
                return Decimal(self.value)
            elif self.value_type == 'string':
                return self.value
            else:
                raise InvalidOperatorArgument(
                    f"Literal({self.value_type})",
                    f"Unknown literal type: {self.value_type}"
                )
        except (ValueError, TypeError) as e:
            raise InvalidOperatorArgument(
                f"Literal({self.value_type})",
                f"Bad format for {self.value_type} literal: {self.value}"
            )


class QuantityEvaluator(DefinitionEvaluator):
    """
    Constructs a quantity (value with unit).
    """

    def __init__(self, value_expr, unit: str):
        self.value_expr = value_expr
        self.unit = unit

    def evaluate(self, context: Context) -> Any:
        """Create quantity."""
        value = self.value_expr.evaluate(context)
        # TODO: Return actual Quantity object
        return {'value': value, 'unit': self.unit}


class RatioEvaluator(DefinitionEvaluator):
    """
    Constructs a ratio (numerator and denominator).
    """

    def __init__(self, numerator_expr, denominator_expr):
        self.numerator_expr = numerator_expr
        self.denominator_expr = denominator_expr

    def evaluate(self, context: Context) -> Any:
        """Create ratio."""
        numerator = self.numerator_expr.evaluate(context)
        denominator = self.denominator_expr.evaluate(context)
        # TODO: Return actual Ratio object
        return {'numerator': numerator, 'denominator': denominator}


class CodeEvaluator(DefinitionEvaluator):
    """
    Creates a code value.
    """

    def __init__(self, code: str, system: str, version: Optional[str] = None, display: Optional[str] = None):
        self.code = code
        self.system = system
        self.version = version
        self.display = display

    def evaluate(self, context: Context) -> Code:
        """Create code."""
        return Code(code=self.code, system=self.system, version=self.version, display=self.display)


class ConceptEvaluator(DefinitionEvaluator):
    """
    Creates a concept (set of codes).
    """

    def __init__(self, codes: List[Code], display: Optional[str] = None):
        self.codes = codes
        self.display = display

    def evaluate(self, context: Context) -> Concept:
        """Create concept."""
        return Concept(codes=self.codes, display=self.display)


class MessageEvaluator(DefinitionEvaluator):
    """
    Evaluates a message/string expression.
    """

    def __init__(self, condition_expr, message_expr: str, severity: str = 'message'):
        self.condition_expr = condition_expr
        self.message_expr = message_expr
        self.severity = severity.lower()

    def evaluate(self, context: Context) -> Any:
        """Evaluate message and optionally log."""
        condition = self.condition_expr.evaluate(context)

        if isinstance(condition, bool) and condition:
            # Log message with appropriate severity
            # TODO: Implement logging
            return True

        return False


class TotalEvaluator(DefinitionEvaluator):
    """
    Evaluates to the total/count of something.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> int:
        """Get total count."""
        operand = self.operand_expr.evaluate(context)

        if operand is None:
            return 0

        if isinstance(operand, (list, tuple)):
            return len(operand)

        # Count non-null iterables
        count = 0
        try:
            for _ in operand:
                count += 1
            return count
        except TypeError:
            return 1 if operand is not None else 0
