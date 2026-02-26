"""
PHI obfuscation evaluators for CQL expressions.

Handles de-identification and redaction of Protected Health Information (PHI).
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class PHIObfuscator(ABC):
    """Base class for PHI obfuscation strategies."""

    @abstractmethod
    def obfuscate(self, value: Any) -> Any:
        """Obfuscate the given value."""
        raise NotImplementedError

    @abstractmethod
    def obfuscate_string(self, value: str) -> str:
        """Obfuscate a string value."""
        raise NotImplementedError

    @abstractmethod
    def obfuscate_number(self, value: float) -> Any:
        """Obfuscate a numeric value."""
        raise NotImplementedError

    @abstractmethod
    def obfuscate_date(self, value: str) -> str:
        """Obfuscate a date value."""
        raise NotImplementedError


class NoOpPHIObfuscator(PHIObfuscator):
    """
    No-op implementation that does not obfuscate any values.
    Used when PHI obfuscation is disabled.
    """

    def obfuscate(self, value: Any) -> Any:
        """Return value unchanged."""
        return value

    def obfuscate_string(self, value: str) -> str:
        """Return string unchanged."""
        return value

    def obfuscate_number(self, value: float) -> Any:
        """Return number unchanged."""
        return value

    def obfuscate_date(self, value: str) -> str:
        """Return date unchanged."""
        return value


class RedactingPHIObfuscator(PHIObfuscator):
    """
    Obfuscator that redacts (removes) PHI values.
    Replaces values with redaction markers.
    """

    # Default redaction markers
    STRING_REDACTION = "[REDACTED]"
    NUMBER_REDACTION = 0
    DATE_REDACTION = "XXXX-XX-XX"

    def __init__(self, string_marker: str = STRING_REDACTION,
                 number_marker: Any = NUMBER_REDACTION,
                 date_marker: str = DATE_REDACTION):
        self.string_marker = string_marker
        self.number_marker = number_marker
        self.date_marker = date_marker

    def obfuscate(self, value: Any) -> Any:
        """Obfuscate value based on type."""
        if value is None:
            return None

        if isinstance(value, str):
            # Check if it's a date-like string
            if self._is_date_string(value):
                return self.obfuscate_date(value)
            return self.obfuscate_string(value)

        if isinstance(value, bool):
            # Booleans are typically not PHI
            return value

        if isinstance(value, (int, float)):
            return self.obfuscate_number(value)

        if isinstance(value, dict):
            # Redact values in dictionaries
            return {k: self.obfuscate(v) for k, v in value.items()}

        if isinstance(value, (list, tuple)):
            # Redact values in lists
            return [self.obfuscate(v) for v in value]

        # Return other types unchanged
        return value

    def obfuscate_string(self, value: str) -> str:
        """Redact string value."""
        return self.string_marker

    def obfuscate_number(self, value: float) -> Any:
        """Redact numeric value."""
        return self.number_marker

    def obfuscate_date(self, value: str) -> str:
        """Redact date value."""
        return self.date_marker

    @staticmethod
    def _is_date_string(value: str) -> bool:
        """Check if string looks like a date."""
        # Simple heuristic: YYYY-MM-DD format
        if len(value) >= 10:
            parts = value.split('-')
            if len(parts) >= 3:
                try:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31
                except (ValueError, IndexError):
                    pass
        return False


class MaskingPHIObfuscator(PHIObfuscator):
    """
    Obfuscator that masks PHI values while preserving type/format.
    """

    def __init__(self, mask_char: str = '*'):
        self.mask_char = mask_char

    def obfuscate(self, value: Any) -> Any:
        """Obfuscate value while preserving structure."""
        if value is None:
            return None

        if isinstance(value, str):
            return self.obfuscate_string(value)

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return self.obfuscate_number(value)

        if isinstance(value, dict):
            return {k: self.obfuscate(v) for k, v in value.items()}

        if isinstance(value, (list, tuple)):
            return [self.obfuscate(v) for v in value]

        return value

    def obfuscate_string(self, value: str) -> str:
        """Mask string with character."""
        if not value:
            return value

        # Keep first and last characters if string is long enough
        if len(value) > 2:
            return value[0] + self.mask_char * (len(value) - 2) + value[-1]

        return self.mask_char * len(value)

    def obfuscate_number(self, value: float) -> Any:
        """Return zero for masked number."""
        return 0

    def obfuscate_date(self, value: str) -> str:
        """Mask date preserving format."""
        if not value or len(value) < 4:
            return value

        # Replace with X's but keep separators
        result = []
        for char in value:
            if char in ('-', '/'):
                result.append(char)
            elif char.isdigit():
                result.append('X')
            else:
                result.append(char)

        return ''.join(result)


class PartialMaskingPHIObfuscator(PHIObfuscator):
    """
    Obfuscator that shows partial information (e.g., last 4 digits).
    """

    def __init__(self, keep_length: int = 4, mask_char: str = '*'):
        self.keep_length = keep_length
        self.mask_char = mask_char

    def obfuscate(self, value: Any) -> Any:
        """Obfuscate value with partial masking."""
        if value is None:
            return None

        if isinstance(value, str):
            return self.obfuscate_string(value)

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return self.obfuscate_number(value)

        if isinstance(value, dict):
            return {k: self.obfuscate(v) for k, v in value.items()}

        if isinstance(value, (list, tuple)):
            return [self.obfuscate(v) for v in value]

        return value

    def obfuscate_string(self, value: str) -> str:
        """Mask string keeping last N characters."""
        if not value or len(value) <= self.keep_length:
            return self.mask_char * len(value)

        mask_length = len(value) - self.keep_length
        return self.mask_char * mask_length + value[-self.keep_length:]

    def obfuscate_number(self, value: float) -> Any:
        """Mask number keeping last digits."""
        str_value = str(int(value)) if isinstance(value, float) else str(value)

        if len(str_value) <= self.keep_length:
            return 0

        mask_length = len(str_value) - self.keep_length
        masked = self.mask_char * mask_length + str_value[-self.keep_length:]

        # Try to return as number
        try:
            return int(masked.replace(self.mask_char, '0'))
        except ValueError:
            return 0

    def obfuscate_date(self, value: str) -> str:
        """Mask date keeping year or month/day."""
        if not value or '-' not in value:
            return self.obfuscate_string(value)

        parts = value.split('-')
        if len(parts) >= 3:
            # Keep year, mask month and day
            return parts[0] + '-XX-XX'

        return self.obfuscate_string(value)


# Factory function for creating obfuscators

def create_obfuscator(strategy: str = 'noop', **kwargs) -> PHIObfuscator:
    """
    Factory function to create PHI obfuscators.

    Args:
        strategy: One of 'noop', 'redact', 'mask', 'partial'
        **kwargs: Strategy-specific parameters

    Returns:
        PHIObfuscator implementation
    """
    strategy = strategy.lower()

    if strategy == 'noop' or strategy == 'none':
        return NoOpPHIObfuscator()

    elif strategy == 'redact':
        return RedactingPHIObfuscator(
            string_marker=kwargs.get('string_marker', '[REDACTED]'),
            number_marker=kwargs.get('number_marker', 0),
            date_marker=kwargs.get('date_marker', 'XXXX-XX-XX')
        )

    elif strategy == 'mask':
        return MaskingPHIObfuscator(
            mask_char=kwargs.get('mask_char', '*')
        )

    elif strategy == 'partial':
        return PartialMaskingPHIObfuscator(
            keep_length=kwargs.get('keep_length', 4),
            mask_char=kwargs.get('mask_char', '*')
        )

    else:
        raise ValueError(f"Unknown obfuscation strategy: {strategy}")


# Convenience classes for evaluation context

class PHIObfuscationContext:
    """Manages PHI obfuscation settings for evaluation."""

    def __init__(self, obfuscator: Optional[PHIObfuscator] = None):
        self.obfuscator = obfuscator or NoOpPHIObfuscator()

    def set_obfuscator(self, obfuscator: PHIObfuscator):
        """Set the obfuscator to use."""
        self.obfuscator = obfuscator

    def obfuscate(self, value: Any) -> Any:
        """Obfuscate value using current obfuscator."""
        return self.obfuscator.obfuscate(value)

    def obfuscate_if_needed(self, value: Any, is_phi: bool = True) -> Any:
        """Obfuscate value only if marked as PHI."""
        if is_phi:
            return self.obfuscate(value)
        return value
