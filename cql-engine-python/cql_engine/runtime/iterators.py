"""Iterator classes for CQL query execution."""

from abc import ABC
from typing import Any, Iterator, List, TypeVar, Generic
from collections.abc import Mapping

T = TypeVar("T")


class ResetIterator(Iterator[T], Generic[T]):
    """Iterator that can be reset to the beginning.

    This iterator caches elements as they are iterated, allowing
    the iteration to be reset and replayed.
    """

    def __init__(self, source: Iterator[T]):
        """Initialize a ResetIterator.

        Args:
            source: The source iterator to wrap
        """
        self.source = source
        self.data: List[T] = []
        self.data_index = -1
        self.data_cached = False

    def __iter__(self) -> Iterator[T]:
        """Return self as iterator."""
        return self

    def __next__(self) -> T:
        """Get the next element."""
        if not self.data_cached:
            element = next(self.source)
            self.data.append(element)
            return element

        self.data_index += 1
        if self.data_index < len(self.data):
            return self.data[self.data_index]
        raise StopIteration

    def has_next(self) -> bool:
        """Check if there are more elements.

        Returns:
            True if there are more elements
        """
        if not self.data_cached:
            try:
                next(self.source)
                # Put it back by restoring source state
                return True
            except StopIteration:
                return False

        return self.data_index < len(self.data) - 1 and len(self.data) > 0

    def reset(self) -> None:
        """Reset the iterator to the beginning.

        This consumes any remaining elements from the source and caches them.
        """
        # Consume remaining elements
        while True:
            try:
                self.data.append(next(self.source))
            except StopIteration:
                break

        self.data_cached = True
        self.data_index = -1


class TimesIterator(Iterator[Any]):
    """Iterator that produces the Cartesian product of two iterators.

    Produces pairs (tuples) of elements from left and right iterators
    in all combinations.
    """

    def __init__(self, left: Iterator[Any], right: Iterator[Any]):
        """Initialize a TimesIterator.

        Args:
            left: The left iterator
            right: The right iterator
        """
        self.left = left
        self.right = ResetIterator(right)
        self.left_needed = True
        self.left_element: Any = None

    def __iter__(self) -> Iterator[Any]:
        """Return self as iterator."""
        return self

    def __next__(self) -> Any:
        """Get the next pair.

        Returns:
            A tuple of (left_element, right_element)
        """
        if not self.has_next():
            raise StopIteration
        return self._next_internal()

    def _next_internal(self) -> Any:
        """Internal next implementation."""
        if self.left_needed:
            self.left_element = next(self.left)
            self.left_needed = False

        result = (self.left_element, next(self.right))
        return result

    def has_next(self) -> bool:
        """Check if there are more pairs.

        Returns:
            True if there are more pairs
        """
        if self.left_needed:
            try:
                return next(self.left) is not None and self.right.has_next()
            except StopIteration:
                return False

        if not self.right.has_next():
            try:
                # Try to get next left element
                self.left_element = next(self.left)
                self.left_needed = False
                self.right.reset()
            except StopIteration:
                return False

        return self.right.has_next()


class QueryIterator(Iterator[List[Any]]):
    """Iterator for CQL query results.

    Combines multiple source iterators into a Cartesian product
    and unpacks the result into lists.
    """

    def __init__(self, context: Any, sources: List[Iterator[Any]]):
        """Initialize a QueryIterator.

        Args:
            context: Execution context
            sources: List of source iterators
        """
        self.result: List[Any] = [None] * len(sources)

        # Build nested TimesIterator for all sources
        self.source_iterator: Iterator[Any] = None
        for i in range(len(sources) - 1, -1, -1):
            if self.source_iterator is None:
                self.source_iterator = sources[i]
            else:
                self.source_iterator = TimesIterator(sources[i], self.source_iterator)

    def __iter__(self) -> Iterator[List[Any]]:
        """Return self as iterator."""
        return self

    def __next__(self) -> List[Any]:
        """Get the next result row.

        Returns:
            A list of values from all source iterators
        """
        return self.unpack(next(self.source_iterator))

    def unpack(self, element: Any) -> List[Any]:
        """Unpack a Cartesian product element into a list.

        Args:
            element: The element from source_iterator

        Returns:
            Unpacked list of values
        """
        self.result = [None] * len(self.result)
        self._unpair(element, self.result, 0)
        return list(self.result)

    @staticmethod
    def _unpair(element: Any, target: List[Any], index: int) -> None:
        """Recursively unpack paired elements.

        Args:
            element: The element to unpack (may be a Mapping.Entry or value)
            target: The target list to populate
            index: The current index in the target list
        """
        if isinstance(element, Mapping):
            # Handle as a mapping (dictionary-like)
            items = list(element.items())
            if items:
                key, value = items[0]
                QueryIterator._unpair(key, target, index)
                QueryIterator._unpair(value, target, index + 1)
        else:
            # Direct value
            target[index] = element
