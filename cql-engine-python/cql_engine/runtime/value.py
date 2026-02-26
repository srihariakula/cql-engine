"""Value utility class for numeric operations."""

from decimal import Decimal, RoundingMode
from typing import Optional


class Value:
    """Utility class for numeric value validation and precision handling."""

    MAX_INT = 2147483647  # Integer.MAX_VALUE in Java
    MIN_INT = -2147483648  # Integer.MIN_VALUE in Java
    MAX_LONG = 9223372036854775807  # Long.MAX_VALUE in Java
    MIN_LONG = -9223372036854775808  # Long.MIN_VALUE in Java
    MAX_DECIMAL = Decimal("9999999999999999999999999999.99999999")
    MIN_DECIMAL = Decimal("-9999999999999999999999999999.99999999")

    @staticmethod
    def verify_precision(value: Decimal, target_scale: Optional[int] = None) -> Decimal:
        """Verify and adjust precision of a decimal value.

        The CQL specification mandates a minimum precision. This implementation
        applies the minimum precision as the maximum precision for consistency.

        Args:
            value: The decimal value to verify
            target_scale: Optional target scale (number of decimal places)

        Returns:
            The value with verified precision
        """
        # At most 8 decimal places
        if value.as_tuple().exponent < -8:
            value = value.quantize(Decimal("0.00000001"), rounding=RoundingMode.FLOOR)

        # At least 0 decimal places
        if value.as_tuple().exponent < 0:
            value = value.quantize(Decimal("1"), rounding=RoundingMode.FLOOR)

        if target_scale is not None and value.as_tuple().exponent < -target_scale:
            value = value.normalize()

        return value

    @staticmethod
    def validate_decimal(ret: Decimal, target_scale: Optional[int] = None) -> Optional[Decimal]:
        """Validate a decimal value against bounds.

        Args:
            ret: The decimal value to validate
            target_scale: Optional target scale

        Returns:
            The validated and verified decimal, or None if out of bounds
        """
        if ret > Value.MAX_DECIMAL or ret < Value.MIN_DECIMAL:
            return None
        return Value.verify_precision(ret, target_scale)

    @staticmethod
    def validate_integer(ret: int | float) -> Optional[int]:
        """Validate an integer value against bounds.

        Args:
            ret: The integer value to validate

        Returns:
            The validated integer, or None if out of bounds
        """
        int_val = int(ret) if isinstance(ret, float) else ret
        if int_val > Value.MAX_INT or int_val < Value.MIN_INT:
            return None
        return int_val

    @staticmethod
    def validate_long(ret: int | float) -> Optional[int]:
        """Validate a long integer value against bounds.

        Args:
            ret: The long integer value to validate

        Returns:
            The validated long integer, or None if out of bounds
        """
        long_val = int(ret) if isinstance(ret, float) else ret
        if long_val > Value.MAX_LONG or long_val < Value.MIN_LONG:
            return None
        return long_val
