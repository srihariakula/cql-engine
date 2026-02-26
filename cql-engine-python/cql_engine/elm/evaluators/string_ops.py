"""
String operation evaluators for CQL ELM execution engine.

This module contains evaluators for string operations including:
- Concatenation: Concatenate, Combine
- Splitting: Split, SplitOnMatches
- Case conversion: Upper, Lower
- Length and position: Length, PositionOf, LastPositionOf
- Substring operations: Substring
- Pattern matching: StartsWith, EndsWith, Matches, ReplaceMatches
- Indexing: Indexer
"""

from abc import ABC
from typing import Any, Optional, List
import re

from cql_engine.exception import InvalidOperatorArgument


class Evaluator(ABC):
    """Base class for all evaluators."""

    def evaluate(self, context: Any) -> Any:
        """Evaluate the expression in the given context."""
        raise NotImplementedError


class ConcatenateEvaluator(Evaluator):
    """
    Concatenate operator evaluator.

    The concatenate (+) operator performs string concatenation of its arguments.
    If either argument is null, the result is null.

    Supports:
    - Concatenate(String, String) -> String
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        left = self.operands[0].evaluate(context)
        right = self.operands[1].evaluate(context)
        return self._concatenate(left, right)

    @staticmethod
    def _concatenate(left: Any, right: Any) -> Optional[str]:
        if left is None or right is None:
            return None

        if isinstance(left, str) and isinstance(right, str):
            return left + right

        raise InvalidOperatorArgument(
            "Concatenate(String, String)",
            f"Concatenate({type(left).__name__}, {type(right).__name__})"
        )


class CombineEvaluator(Evaluator):
    """
    Combine operator evaluator.

    The Combine operator performs string concatenation on a list of strings,
    separated by an optional separator string.

    Supports:
    - Combine(List<String>) -> String
    - Combine(List<String>, separator String) -> String
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        strings = self.operands[0].evaluate(context)
        separator = self.operands[1].evaluate(context) if len(self.operands) > 1 else None
        return self._combine(strings, separator)

    @staticmethod
    def _combine(strings: Any, separator: Optional[str] = None) -> Optional[str]:
        if strings is None:
            return None

        if isinstance(strings, (list, tuple)):
            if separator is None:
                separator = ""
            return separator.join(str(s) if s is not None else "" for s in strings)

        raise InvalidOperatorArgument(
            "Combine(List<String>) or Combine(List<String>, String)",
            f"Combine({type(strings).__name__})"
        )


class SplitEvaluator(Evaluator):
    """
    Split operator evaluator.

    The Split operator splits a string into a list of strings using a separator.
    If the stringToSplit argument is null, the result is null.
    If the stringToSplit argument does not contain any appearances of the separator,
    the result is a list of strings containing one element that is the value of
    the stringToSplit argument.

    Supports:
    - Split(String, separator String) -> List<String>
    """

    def __init__(self, string_to_split, separator):
        self.string_to_split = string_to_split
        self.separator = separator

    def evaluate(self, context: Any) -> Any:
        string_value = self.string_to_split.evaluate(context)
        separator_value = self.separator.evaluate(context)
        return self._split(string_value, separator_value)

    @staticmethod
    def _split(string_to_split: Any, separator: Any) -> Optional[List[str]]:
        if string_to_split is None:
            return None

        if isinstance(string_to_split, str):
            if separator is None:
                return [string_to_split]
            else:
                # Use str.split() which handles separators well
                return string_to_split.split(str(separator))

        raise InvalidOperatorArgument(
            "Split(String, String)",
            f"Split({type(string_to_split).__name__}, {type(separator).__name__})"
        )


class SplitOnMatchesEvaluator(Evaluator):
    """
    SplitOnMatches operator evaluator.

    The SplitOnMatches operator splits a string into a list of strings using
    a regular expression pattern as separator.

    Supports:
    - SplitOnMatches(String, pattern String) -> List<String>
    """

    def __init__(self, string_value, pattern):
        self.string_value = string_value
        self.pattern = pattern

    def evaluate(self, context: Any) -> Any:
        string_val = self.string_value.evaluate(context)
        pattern_val = self.pattern.evaluate(context)
        return self._split_on_matches(string_val, pattern_val)

    @staticmethod
    def _split_on_matches(string_val: Any, pattern: Any) -> Optional[List[str]]:
        if string_val is None:
            return None

        if isinstance(string_val, str) and isinstance(pattern, str):
            try:
                return re.split(pattern, string_val)
            except re.error:
                return None

        raise InvalidOperatorArgument(
            "SplitOnMatches(String, String)",
            f"SplitOnMatches({type(string_val).__name__}, {type(pattern).__name__})"
        )


class LengthEvaluator(Evaluator):
    """
    Length operator evaluator.

    For strings: returns the number of characters.
    For lists: returns the number of elements.

    Supports:
    - Length(String) -> Integer
    - Length(List<T>) -> Integer
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._length(operand)

    @staticmethod
    def _length(operand: Any) -> Optional[int]:
        if isinstance(operand, str):
            return len(operand) if operand is not None else None

        if isinstance(operand, (list, tuple)):
            return 0 if operand is None else len(operand)

        raise InvalidOperatorArgument(
            "Length(String) or Length(List<T>)",
            f"Length({type(operand).__name__})"
        )


class UpperEvaluator(Evaluator):
    """
    Upper operator evaluator.

    The Upper operator returns the upper case of its argument.
    If the argument is null, the result is null.

    Supports:
    - Upper(String) -> String
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._upper(operand)

    @staticmethod
    def _upper(operand: Any) -> Optional[str]:
        if operand is None:
            return None

        if isinstance(operand, str):
            return operand.upper()

        raise InvalidOperatorArgument(
            "Upper(String)",
            f"Upper({type(operand).__name__})"
        )


class LowerEvaluator(Evaluator):
    """
    Lower operator evaluator.

    The Lower operator returns the lower case of its argument.
    If the argument is null, the result is null.

    Supports:
    - Lower(String) -> String
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context: Any) -> Any:
        operand = self.operand.evaluate(context)
        return self._lower(operand)

    @staticmethod
    def _lower(operand: Any) -> Optional[str]:
        if operand is None:
            return None

        if isinstance(operand, str):
            return operand.lower()

        raise InvalidOperatorArgument(
            "Lower(String)",
            f"Lower({type(operand).__name__})"
        )


class PositionOfEvaluator(Evaluator):
    """
    PositionOf operator evaluator.

    The PositionOf operator returns the 0-based index of the given pattern in the given string.
    If the pattern is not found, the result is -1.
    If either argument is null, the result is null.

    Supports:
    - PositionOf(pattern String, argument String) -> Integer
    """

    def __init__(self, pattern, string):
        self.pattern = pattern
        self.string = string

    def evaluate(self, context: Any) -> Any:
        pattern_val = self.pattern.evaluate(context)
        string_val = self.string.evaluate(context)
        return self._position_of(pattern_val, string_val)

    @staticmethod
    def _position_of(pattern: Any, string: Any) -> Optional[int]:
        if pattern is None or string is None:
            return None

        if isinstance(pattern, str) and isinstance(string, str):
            index = string.find(pattern)
            return index if index >= 0 else -1

        raise InvalidOperatorArgument(
            "PositionOf(String, String)",
            f"PositionOf({type(pattern).__name__}, {type(string).__name__})"
        )


class LastPositionOfEvaluator(Evaluator):
    """
    LastPositionOf operator evaluator.

    The LastPositionOf operator returns the 0-based index of the last occurrence
    of the given pattern in the given string.
    If the pattern is not found, the result is -1.
    If either argument is null, the result is null.

    Supports:
    - LastPositionOf(pattern String, argument String) -> Integer
    """

    def __init__(self, pattern, string):
        self.pattern = pattern
        self.string = string

    def evaluate(self, context: Any) -> Any:
        pattern_val = self.pattern.evaluate(context)
        string_val = self.string.evaluate(context)
        return self._last_position_of(pattern_val, string_val)

    @staticmethod
    def _last_position_of(pattern: Any, string: Any) -> Optional[int]:
        if pattern is None or string is None:
            return None

        if isinstance(pattern, str) and isinstance(string, str):
            index = string.rfind(pattern)
            return index if index >= 0 else -1

        raise InvalidOperatorArgument(
            "LastPositionOf(String, String)",
            f"LastPositionOf({type(pattern).__name__}, {type(string).__name__})"
        )


class SubstringEvaluator(Evaluator):
    """
    Substring operator evaluator.

    The Substring operator returns the string within stringToSub, starting at the
    0-based index startIndex, and consisting of length characters.
    If length is omitted, the substring returned starts at startIndex and continues
    to the end of stringToSub.
    If stringToSub or startIndex is null, or startIndex is out of range, the result is null.

    Supports:
    - Substring(stringToSub String, startIndex Integer) -> String
    - Substring(stringToSub String, startIndex Integer, length Integer) -> String
    """

    def __init__(self, string_to_sub, start_index, length=None):
        self.string_to_sub = string_to_sub
        self.start_index = start_index
        self.length = length

    def evaluate(self, context: Any) -> Any:
        string_val = self.string_to_sub.evaluate(context)
        start_index_val = self.start_index.evaluate(context)
        length_val = None if self.length is None else self.length.evaluate(context)
        return self._substring(string_val, start_index_val, length_val)

    @staticmethod
    def _substring(string_value: Any, start_index: Any, length: Any = None) -> Optional[str]:
        if string_value is None or start_index is None:
            return None

        if isinstance(string_value, str) and isinstance(start_index, int):
            if start_index < 0 or start_index >= len(string_value):
                return None

            if length is None:
                return string_value[start_index:]
            else:
                end_index = start_index + length
                if end_index > len(string_value):
                    end_index = len(string_value)
                if end_index < start_index:
                    end_index = start_index
                return string_value[start_index:end_index]

        raise InvalidOperatorArgument(
            "Substring(String, Integer) or Substring(String, Integer, Integer)",
            f"Substring({type(string_value).__name__}, {type(start_index).__name__})"
        )


class StartsWithEvaluator(Evaluator):
    """
    StartsWith operator evaluator.

    The StartsWith operator returns true if the given string starts with the given prefix.
    If the prefix is the empty string, the result is true.
    If either argument is null, the result is null.

    Supports:
    - StartsWith(String, prefix String) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        argument = self.operands[0].evaluate(context)
        prefix = self.operands[1].evaluate(context)
        return self._starts_with(argument, prefix)

    @staticmethod
    def _starts_with(argument: Any, prefix: Any) -> Optional[bool]:
        if argument is None or prefix is None:
            return None

        if isinstance(argument, str) and isinstance(prefix, str):
            return argument.startswith(prefix)

        raise InvalidOperatorArgument(
            "StartsWith(String, String)",
            f"StartsWith({type(argument).__name__}, {type(prefix).__name__})"
        )


class EndsWithEvaluator(Evaluator):
    """
    EndsWith operator evaluator.

    The EndsWith operator returns true if the given string ends with the given suffix.
    If the suffix is the empty string, the result is true.
    If either argument is null, the result is null.

    Supports:
    - EndsWith(String, suffix String) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        argument = self.operands[0].evaluate(context)
        suffix = self.operands[1].evaluate(context)
        return self._ends_with(argument, suffix)

    @staticmethod
    def _ends_with(argument: Any, suffix: Any) -> Optional[bool]:
        if argument is None or suffix is None:
            return None

        if isinstance(argument, str) and isinstance(suffix, str):
            return argument.endswith(suffix)

        raise InvalidOperatorArgument(
            "EndsWith(String, String)",
            f"EndsWith({type(argument).__name__}, {type(suffix).__name__})"
        )


class MatchesEvaluator(Evaluator):
    """
    Matches operator evaluator.

    The Matches operator returns true if the given string matches the given regex pattern.
    If either argument is null, the result is null.

    Supports:
    - Matches(String, pattern String) -> Boolean
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        argument = self.operands[0].evaluate(context)
        pattern = self.operands[1].evaluate(context)
        return self._matches(argument, pattern)

    @staticmethod
    def _matches(argument: Any, pattern: Any) -> Optional[bool]:
        if argument is None or pattern is None:
            return None

        if isinstance(argument, str) and isinstance(pattern, str):
            try:
                return bool(re.fullmatch(pattern, argument))
            except re.error:
                return False

        raise InvalidOperatorArgument(
            "Matches(String, String)",
            f"Matches({type(argument).__name__}, {type(pattern).__name__})"
        )


class ReplaceMatchesEvaluator(Evaluator):
    """
    ReplaceMatches operator evaluator.

    The ReplaceMatches operator returns a new string where all non-overlapping
    matches of the given regex pattern are replaced with the replacement string.

    Supports:
    - ReplaceMatches(argument String, pattern String, replacement String) -> String
    """

    def __init__(self, argument, pattern, replacement):
        self.argument = argument
        self.pattern = pattern
        self.replacement = replacement

    def evaluate(self, context: Any) -> Any:
        argument_val = self.argument.evaluate(context)
        pattern_val = self.pattern.evaluate(context)
        replacement_val = self.replacement.evaluate(context)
        return self._replace_matches(argument_val, pattern_val, replacement_val)

    @staticmethod
    def _replace_matches(argument: Any, pattern: Any, replacement: Any) -> Optional[str]:
        if argument is None or pattern is None or replacement is None:
            return None

        if isinstance(argument, str) and isinstance(pattern, str) and isinstance(replacement, str):
            try:
                return re.sub(pattern, replacement, argument)
            except re.error:
                return None

        raise InvalidOperatorArgument(
            "ReplaceMatches(String, String, String)",
            f"ReplaceMatches({type(argument).__name__}, {type(pattern).__name__}, {type(replacement).__name__})"
        )


class IndexerEvaluator(Evaluator):
    """
    Indexer operator evaluator.

    The Indexer operator accesses elements in a list or characters in a string by index.
    The index is 0-based. If the index is out of range, the result is null.

    Supports:
    - Indexer(List<T>, index Integer) -> T
    - Indexer(String, index Integer) -> String
    """

    def __init__(self, operands: list):
        self.operands = operands

    def evaluate(self, context: Any) -> Any:
        operand = self.operands[0].evaluate(context)
        index = self.operands[1].evaluate(context)
        return self._indexer(operand, index)

    @staticmethod
    def _indexer(operand: Any, index: Any) -> Optional[Any]:
        if operand is None or index is None:
            return None

        if isinstance(operand, str) and isinstance(index, int):
            if 0 <= index < len(operand):
                return operand[index]
            return None

        if isinstance(operand, (list, tuple)) and isinstance(index, int):
            if 0 <= index < len(operand):
                return operand[index]
            return None

        raise InvalidOperatorArgument(
            "Indexer(List<T>, Integer) or Indexer(String, Integer)",
            f"Indexer({type(operand).__name__}, {type(index).__name__})"
        )
