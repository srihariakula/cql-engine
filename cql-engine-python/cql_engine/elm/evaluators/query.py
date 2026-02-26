"""
Query and iteration evaluators for CQL expressions.

Handles query expressions, filtering, sorting, and iteration operations.
"""

from abc import ABC
from typing import Any, Optional, List, Dict
from collections import OrderedDict

from cql_engine.execution.context import Context
from cql_engine.execution.exceptions import InvalidOperatorArgument
from cql_engine.runtime.tuple import Tuple


class QueryEvaluator(ABC):
    """Base class for query evaluators."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the query."""
        raise NotImplementedError


class QueryExpressionEvaluator(QueryEvaluator):
    """
    Main query evaluator handling multi-source queries with filtering, sorting, etc.

    Supports:
    - Multiple sources (FROM clauses)
    - Let clauses for intermediate computations
    - Relationships (WITH/WITHOUT)
    - Where clause filtering
    - Sorting
    - Return expressions
    """

    def __init__(self, sources: List[tuple], let_clauses: Optional[List[tuple]] = None,
                 relationship_clauses: Optional[List[tuple]] = None,
                 where_expr = None, return_expr = None, sort_expr = None):
        self.sources = sources  # List of (alias, expression) tuples
        self.let_clauses = let_clauses or []
        self.relationship_clauses = relationship_clauses or []
        self.where_expr = where_expr
        self.return_expr = return_expr
        self.sort_expr = sort_expr

    def evaluate(self, context: Context) -> Any:
        """Evaluate the query expression."""
        # TODO: Implement full query evaluation with nested iteration
        # This is a simplified version
        results = []

        # Process each source
        for alias, source_expr in self.sources:
            source_data = source_expr.evaluate(context)

            # Convert single values to iterable
            if not isinstance(source_data, (list, tuple)):
                if hasattr(source_data, '__iter__'):
                    source_data = list(source_data)
                else:
                    source_data = [source_data] if source_data is not None else []

            # Process each element
            for item in source_data:
                # Push variable context
                context.push_variable(alias, item)
                try:
                    # Evaluate let clauses
                    for let_alias, let_expr in self.let_clauses:
                        let_value = let_expr.evaluate(context)
                        context.push_variable(let_alias, let_value)

                    # Evaluate relationships
                    if self._evaluate_relationships(context):
                        # Evaluate where clause
                        if self.where_expr is None or self._evaluate_where(context):
                            # Evaluate return
                            result = self._evaluate_return(context, alias, item)
                            if result is not None:
                                results.append(result)

                finally:
                    # Pop let variables
                    for _ in self.let_clauses:
                        context.pop_variable()
                    # Pop source variable
                    context.pop_variable()

        # Remove duplicates if needed
        results = self._distinct_if_needed(results, context)

        # Sort results
        if self.sort_expr:
            results = self._sort_results(results, context)

        # Return results
        if not results:
            return None

        return results if len(self.sources) > 1 else (results[0] if results else None)

    def _evaluate_relationships(self, context: Context) -> bool:
        """Evaluate WITH/WITHOUT relationships."""
        for relationship in self.relationship_clauses:
            # TODO: Implement relationship evaluation
            pass
        return True

    def _evaluate_where(self, context: Context) -> bool:
        """Evaluate WHERE clause."""
        if self.where_expr is None:
            return True

        result = self.where_expr.evaluate(context)
        return isinstance(result, bool) and result

    def _evaluate_return(self, context: Context, alias: str, item: Any) -> Any:
        """Evaluate RETURN clause or construct tuple."""
        if self.return_expr:
            return self.return_expr.evaluate(context)

        # Default: return the item
        return item

    def _distinct_if_needed(self, results: List[Any], context: Context) -> List[Any]:
        """Remove duplicates if return is marked as distinct."""
        # TODO: Check if return is distinct
        return results

    def _sort_results(self, results: List[Any], context: Context) -> List[Any]:
        """Sort results according to sort clause."""
        # TODO: Implement sorting
        return results


class AliasedQuerySourceEvaluator(QueryEvaluator):
    """Represents an aliased source in a query."""

    def __init__(self, alias: str, source_expr):
        self.alias = alias
        self.source_expr = source_expr

    def evaluate(self, context: Context) -> Any:
        return self.source_expr.evaluate(context)


class QueryLetRefEvaluator(QueryEvaluator):
    """
    References a let clause variable in a query.
    """

    def __init__(self, ref_name: str):
        self.ref_name = ref_name

    def evaluate(self, context: Context) -> Any:
        return context.resolve_variable(self.ref_name, is_let=True).get_value()


class AliasRefEvaluator(QueryEvaluator):
    """
    References an alias (source variable) in a query.
    """

    def __init__(self, ref_name: str):
        self.ref_name = ref_name

    def evaluate(self, context: Context) -> Any:
        return context.resolve_variable(self.ref_name).get_value()


class WithEvaluator(QueryEvaluator):
    """
    WITH clause: includes rows where a relationship condition is satisfied.
    """

    def __init__(self, alias: str, expression, such_that_expr):
        self.alias = alias
        self.expression = expression
        self.such_that_expr = such_that_expr

    def evaluate(self, context: Context) -> bool:
        """Check if WITH condition is satisfied."""
        related_data = self.expression.evaluate(context)

        if not isinstance(related_data, (list, tuple)):
            related_data = [related_data] if related_data else []

        for item in related_data:
            context.push_variable(self.alias, item)
            try:
                condition = self.such_that_expr.evaluate(context)
                if isinstance(condition, bool) and condition:
                    return True
            finally:
                context.pop_variable()

        return False


class WithoutEvaluator(QueryEvaluator):
    """
    WITHOUT clause: includes rows where a relationship condition is NOT satisfied.
    """

    def __init__(self, alias: str, expression, such_that_expr):
        self.alias = alias
        self.expression = expression
        self.such_that_expr = such_that_expr

    def evaluate(self, context: Context) -> bool:
        """Check if WITHOUT condition is satisfied."""
        with_result = WithEvaluator(self.alias, self.expression, self.such_that_expr).evaluate(context)
        return not with_result


class WhereEvaluator(QueryEvaluator):
    """
    WHERE clause: filters rows based on a condition.
    """

    def __init__(self, condition_expr):
        self.condition_expr = condition_expr

    def evaluate(self, context: Context) -> bool:
        """Evaluate WHERE condition."""
        result = self.condition_expr.evaluate(context)
        return isinstance(result, bool) and result


class ReturnEvaluator(QueryEvaluator):
    """
    RETURN clause: specifies what to return for each row.
    """

    def __init__(self, expression, is_distinct: bool = False):
        self.expression = expression
        self.is_distinct = is_distinct

    def evaluate(self, context: Context) -> Any:
        """Evaluate RETURN expression."""
        return self.expression.evaluate(context)


class SortEvaluator(QueryEvaluator):
    """
    SORT clause: sorts results.
    """

    def __init__(self, sort_items: List[tuple]):
        self.sort_items = sort_items  # List of (by_item, direction) tuples

    def evaluate(self, context: Context) -> List[Any]:
        """This is applied after query execution."""
        # TODO: Implement sorting logic
        pass


class SortClauseEvaluator(QueryEvaluator):
    """Represents a sort clause with multiple sort items."""

    def __init__(self, by_items: List['SortByItem']):
        self.by_items = by_items

    def evaluate(self, context: Context) -> List[Any]:
        """Apply sorting."""
        # TODO: Implement
        pass


class ByDirectionEvaluator(QueryEvaluator):
    """Specifies sort direction (ascending/descending)."""

    def __init__(self, direction: str):
        self.direction = direction.lower()  # 'asc' or 'desc'

    def evaluate(self, context: Context) -> str:
        return self.direction


class ByColumnEvaluator(QueryEvaluator):
    """Sort by a column path."""

    def __init__(self, path: str):
        self.path = path

    def evaluate(self, context: Context) -> str:
        return self.path


class ByExpressionEvaluator(QueryEvaluator):
    """Sort by an expression result."""

    def __init__(self, expression):
        self.expression = expression

    def evaluate(self, context: Context) -> Any:
        return self.expression.evaluate(context)


class ForEachEvaluator(QueryEvaluator):
    """
    FOREACH clause: iterates over elements and evaluates an expression for each.
    """

    def __init__(self, source_expr, iterator_name: str, body_expr):
        self.source_expr = source_expr
        self.iterator_name = iterator_name
        self.body_expr = body_expr

    def evaluate(self, context: Context) -> List[Any]:
        """Evaluate ForEach."""
        source = self.source_expr.evaluate(context)

        if source is None:
            return None

        if not isinstance(source, (list, tuple)):
            source = [source]

        results = []
        for item in source:
            context.push_variable(self.iterator_name, item)
            try:
                result = self.body_expr.evaluate(context)
                results.append(result)
            finally:
                context.pop_variable()

        return results


class FilterEvaluator(QueryEvaluator):
    """
    FILTER: filters a list based on a condition using an iterator.
    """

    def __init__(self, source_expr, iterator_name: str, condition_expr):
        self.source_expr = source_expr
        self.iterator_name = iterator_name
        self.condition_expr = condition_expr

    def evaluate(self, context: Context) -> List[Any]:
        """Filter list elements."""
        source = self.source_expr.evaluate(context)

        if source is None:
            return None

        if not isinstance(source, (list, tuple)):
            source = [source]

        results = []
        for item in source:
            context.push_variable(self.iterator_name, item)
            try:
                condition = self.condition_expr.evaluate(context)
                if isinstance(condition, bool) and condition:
                    results.append(item)
            finally:
                context.pop_variable()

        return results


class TimesEvaluator(QueryEvaluator):
    """
    Cartesian product of multiple sources (TIMES operation).
    """

    def __init__(self, sources: List[tuple]):
        self.sources = sources  # List of (alias, expression) tuples

    def evaluate(self, context: Context) -> List[tuple]:
        """Compute Cartesian product."""
        if not self.sources:
            return []

        # Evaluate all sources
        source_data = []
        for alias, expr in self.sources:
            data = expr.evaluate(context)
            if not isinstance(data, (list, tuple)):
                data = [data] if data is not None else []
            source_data.append((alias, data))

        # Compute Cartesian product
        results = []
        self._cartesian_product(source_data, 0, {}, results, context)
        return results

    def _cartesian_product(self, sources, index, current, results, context):
        """Recursively compute Cartesian product."""
        if index == len(sources):
            # Create result tuple
            results.append(tuple(current.values()))
            return

        alias, data = sources[index]
        for item in data:
            current[alias] = item
            self._cartesian_product(sources, index + 1, current, results, context)
