"""CQL List utility for list operations."""

from typing import Any, Callable, Iterable, Iterator, Optional, TypeVar, Generic

T = TypeVar("T")


class CqlList(Generic[T]):
    """Utility class for CQL list operations and comparisons.

    Provides methods for comparing and working with CQL lists.
    """

    def __init__(
        self,
        context: Optional[Any] = None,
        alias: Optional[str] = None,
        expression: Optional[Any] = None,
        path: Optional[str] = None,
    ):
        """Initialize a CqlList.

        Args:
            context: Optional execution context
            alias: Optional variable alias
            expression: Optional expression to evaluate
            path: Optional path for column access
        """
        self.context = context
        self.alias = alias
        self.expression = expression
        self.path = path

    def value_sort(self, left: Any, right: Any) -> int:
        """Comparator for sorting values.

        Args:
            left: First value
            right: Second value

        Returns:
            -1 if left < right, 0 if equal, 1 if left > right
        """
        return self.compare_to(left, right)

    def expression_sort(self, left: Any, right: Any) -> int:
        """Comparator for sorting by expression evaluation.

        Args:
            left: First value
            right: Second value

        Returns:
            -1 if left < right, 0 if equal, 1 if left > right
        """
        if self.context is None or self.expression is None:
            return self.compare_to(left, right)

        # Evaluate expression with left context
        try:
            from .execution import Variable

            self.context.push(Variable(name=self.alias, value=left))
            left_eval = self.expression.evaluate(self.context)
        finally:
            self.context.pop()

        # Evaluate expression with right context
        try:
            from .execution import Variable

            self.context.push(Variable(name=self.alias, value=right))
            right_eval = self.expression.evaluate(self.context)
        finally:
            self.context.pop()

        return self.compare_to(left_eval, right_eval)

    def column_sort(self, left: Any, right: Any) -> int:
        """Comparator for sorting by column path.

        Args:
            left: First value
            right: Second value

        Returns:
            -1 if left < right, 0 if equal, 1 if left > right
        """
        if self.context is None or self.path is None:
            return self.compare_to(left, right)

        left_col = self.context.resolve_path(left, self.path)
        right_col = self.context.resolve_path(right, self.path)

        return self.compare_to(left_col, right_col)

    @staticmethod
    def compare_to(left: Any, right: Any) -> int:
        """Compare two values.

        Args:
            left: First value
            right: Second value

        Returns:
            -1 if left < right, 0 if equal, 1 if left > right

        Raises:
            TypeError: If types are not comparable
        """
        if left is None and right is None:
            return 0
        elif left is None:
            return -1
        elif right is None:
            return 1

        try:
            if left < right:
                return -1
            elif left > right:
                return 1
            else:
                return 0
        except TypeError:
            raise TypeError(f"Type {type(left).__name__} is not comparable")

    @staticmethod
    def equivalent(
        left: Iterable[Any], right: Iterable[Any], context: Optional[Any] = None
    ) -> bool:
        """Check if two iterables are equivalent.

        Args:
            left: First iterable
            right: Second iterable
            context: Optional execution context

        Returns:
            True if all elements are equivalent
        """
        left_iter = iter(left)
        right_iter = iter(right)

        for left_obj in left_iter:
            try:
                right_obj = next(right_iter)
            except StopIteration:
                return False

            # Check equivalence
            if hasattr(left_obj, "equivalent"):
                if not left_obj.equivalent(right_obj):
                    return False
            elif left_obj != right_obj:
                return False

        # Check if right has more elements
        try:
            next(right_iter)
            return False
        except StopIteration:
            return True

    @staticmethod
    def equal(
        left: Iterable[Any], right: Iterable[Any], context: Optional[Any] = None
    ) -> Optional[bool]:
        """Check if two iterables are equal.

        Args:
            left: First iterable
            right: Second iterable
            context: Optional execution context

        Returns:
            True if equal, False if not, None if uncertain
        """
        left_iter = iter(left)
        right_iter = iter(right)

        for left_obj in left_iter:
            try:
                right_obj = next(right_iter)
            except StopIteration:
                if left_obj is None:
                    return None
                return False

            # Handle nested iterables
            if isinstance(left_obj, (list, tuple)) and isinstance(right_obj, (list, tuple)):
                result = CqlList.equal(left_obj, right_obj, context)
                if result is not None and not result:
                    return False
                continue

            # Check equality
            if hasattr(left_obj, "equal"):
                result = left_obj.equal(right_obj)
            else:
                result = left_obj == right_obj

            if result is None or not result:
                return result

        # Check if right has more elements
        try:
            next_obj = next(right_iter)
            return None if next_obj is None else False
        except StopIteration:
            return True

    @staticmethod
    def to_list(
        iterable: Iterable[T], include_null_elements: bool = False
    ) -> list[T]:
        """Convert an iterable to a list.

        Args:
            iterable: The iterable to convert
            include_null_elements: Whether to include None values

        Returns:
            List of elements
        """
        result = []
        for element in iterable:
            if element is not None or include_null_elements:
                result.append(element)
        return result
