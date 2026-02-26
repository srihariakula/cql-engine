"""
Temporal evaluators for CQL expressions.

Handles Date, DateTime, Time construction and temporal operations.
"""

from abc import ABC
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Optional

from cql_engine.runtime.temporal import (
    Date,
    DateTime,
    Time,
    Precision,
    BaseTemporal,
)
from cql_engine.runtime.interval import Interval
from cql_engine.execution.context import Context
from cql_engine.execution.exceptions import InvalidOperatorArgument


class TemporalEvaluator(ABC):
    """Base class for temporal evaluators."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the temporal expression."""
        raise NotImplementedError


class DateEvaluator(TemporalEvaluator):
    """
    Constructs a Date from year, month, and day components.

    year is required. month and day default to 1 if not provided.
    Precision is set based on which components are provided.
    """

    def __init__(self, year_expr, month_expr=None, day_expr=None):
        self.year_expr = year_expr
        self.month_expr = month_expr
        self.day_expr = day_expr

    def evaluate(self, context: Context) -> Optional[Date]:
        year = self.year_expr.evaluate(context) if self.year_expr else None

        if year is None:
            return None

        precision = Precision.YEAR

        month = self.month_expr.evaluate(context) if self.month_expr else None
        if month is None:
            month = 1
        else:
            precision = Precision.MONTH

        day = self.day_expr.evaluate(context) if self.day_expr else None
        if day is None:
            day = 1
        else:
            precision = Precision.DAY

        result = Date(year, month, day)
        result.set_precision(precision)
        return result


class DateTimeEvaluator(TemporalEvaluator):
    """
    Constructs a DateTime from year, month, day, hour, minute, second, millisecond,
    and timezone offset components.

    year is required. Other components are optional.
    """

    def __init__(self, year_expr, month_expr=None, day_expr=None,
                 hour_expr=None, minute_expr=None, second_expr=None,
                 millisecond_expr=None, timezone_offset_expr=None):
        self.year_expr = year_expr
        self.month_expr = month_expr
        self.day_expr = day_expr
        self.hour_expr = hour_expr
        self.minute_expr = minute_expr
        self.second_expr = second_expr
        self.millisecond_expr = millisecond_expr
        self.timezone_offset_expr = timezone_offset_expr

    def evaluate(self, context: Context) -> Optional[DateTime]:
        year = self.year_expr.evaluate(context) if self.year_expr else None

        if year is None:
            return None

        # Evaluate all components
        components = [year]

        month = self.month_expr.evaluate(context) if self.month_expr else None
        components.append(month)

        day = self.day_expr.evaluate(context) if self.day_expr else None
        components.append(day)

        hour = self.hour_expr.evaluate(context) if self.hour_expr else None
        components.append(hour)

        minute = self.minute_expr.evaluate(context) if self.minute_expr else None
        components.append(minute)

        second = self.second_expr.evaluate(context) if self.second_expr else None
        components.append(second)

        millisecond = self.millisecond_expr.evaluate(context) if self.millisecond_expr else None
        components.append(millisecond)

        offset = None
        if self.timezone_offset_expr:
            offset = self.timezone_offset_expr.evaluate(context)

        # Clean the array (remove trailing None values)
        components = self._clean_array(components)

        return DateTime(offset, components)

    @staticmethod
    def _clean_array(components: list) -> list:
        """Remove trailing None values from component array."""
        while components and components[-1] is None:
            components.pop()
        return components


class TimeEvaluator(TemporalEvaluator):
    """
    Constructs a Time from hour, minute, second, and millisecond components.

    hour is required. Other components are optional.
    """

    def __init__(self, hour_expr, minute_expr=None, second_expr=None, millisecond_expr=None):
        self.hour_expr = hour_expr
        self.minute_expr = minute_expr
        self.second_expr = second_expr
        self.millisecond_expr = millisecond_expr

    def evaluate(self, context: Context) -> Optional[Time]:
        hour = self.hour_expr.evaluate(context) if self.hour_expr else None

        if hour is None:
            return None

        minute = self.minute_expr.evaluate(context) if self.minute_expr else None
        second = self.second_expr.evaluate(context) if self.second_expr else None
        millisecond = self.millisecond_expr.evaluate(context) if self.millisecond_expr else None

        components = [hour, minute, second, millisecond]
        # Clean trailing None values
        while components and components[-1] is None:
            components.pop()

        return Time(*components)


class NowEvaluator(TemporalEvaluator):
    """
    Returns the date and time of the evaluation request start timestamp.

    This ensures the same value is returned throughout an evaluation request.
    """

    def evaluate(self, context: Context) -> DateTime:
        return context.get_evaluation_datetime()


class TodayEvaluator(TemporalEvaluator):
    """
    Returns the date (with no time component) of the evaluation request start timestamp.
    """

    def evaluate(self, context: Context) -> Optional[Date]:
        return DateFromEvaluator.date_from(context.get_evaluation_datetime())


class TimeOfDayEvaluator(TemporalEvaluator):
    """
    Returns the time of day of the evaluation request start timestamp.
    """

    def evaluate(self, context: Context) -> Optional[Time]:
        return TimeFromEvaluator.time_from(context.get_evaluation_datetime())


class DateFromEvaluator(TemporalEvaluator):
    """
    Extracts the date portion from a DateTime value.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Date]:
        operand = self.operand_expr.evaluate(context)
        return self.date_from(operand)

    @staticmethod
    def date_from(operand: Any) -> Optional[Date]:
        """Extract date from operand."""
        if operand is None:
            return None

        if isinstance(operand, DateTime):
            dt = operand.get_datetime()
            precision = operand.get_precision()

            if precision.to_datetime_index() < 1:
                result = Date(dt.year, 1, 1)
                result.set_precision(Precision.YEAR)
                return result
            elif precision.to_datetime_index() < 2:
                result = Date(dt.year, dt.month, 1)
                result.set_precision(Precision.MONTH)
                return result
            else:
                result = Date(dt.year, dt.month, dt.day)
                result.set_precision(Precision.DAY)
                return result

        raise InvalidOperatorArgument(
            "date_from(DateTime)",
            f"date_from({type(operand).__name__})"
        )


class TimeFromEvaluator(TemporalEvaluator):
    """
    Extracts the time portion from a DateTime value.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Time]:
        operand = self.operand_expr.evaluate(context)
        return self.time_from(operand)

    @staticmethod
    def time_from(operand: Any) -> Optional[Time]:
        """Extract time from operand."""
        if operand is None:
            return None

        if isinstance(operand, DateTime):
            dt = operand.get_datetime()
            precision = operand.get_precision()

            if precision.to_datetime_index() > 2:
                hour = dt.hour
            else:
                return None

            if precision.to_datetime_index() > 3:
                minute = dt.minute
            else:
                return Time(hour)

            if precision.to_datetime_index() > 4:
                second = dt.second
            else:
                return Time(hour, minute)

            if precision.to_datetime_index() > 5:
                millisecond = dt.microsecond // 1000
            else:
                return Time(hour, minute, second)

            return Time(hour, minute, second, millisecond)

        raise InvalidOperatorArgument(
            "time_from(DateTime)",
            f"time_from({type(operand).__name__})"
        )


class DateTimeComponentFromEvaluator(TemporalEvaluator):
    """
    Extracts a specific component (year, month, day, hour, etc.) from a temporal value.
    """

    def __init__(self, operand_expr, precision_str: str):
        self.operand_expr = operand_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[int]:
        operand = self.operand_expr.evaluate(context)
        return self.datetime_component_from(operand, self.precision_str)

    @staticmethod
    def datetime_component_from(operand: Any, precision: str) -> Optional[int]:
        """Extract component from temporal value."""
        if operand is None:
            return None

        if precision is None:
            raise InvalidOperatorArgument(
                "Precision must be specified for the component from operation."
            )

        p = Precision.from_string(precision)

        if isinstance(operand, Date):
            date_obj = operand.get_date()

            if p.to_date_index() > operand.get_precision().to_date_index():
                return None

            if p == Precision.YEAR:
                return date_obj.year
            elif p == Precision.MONTH:
                return date_obj.month
            elif p == Precision.DAY:
                return date_obj.day

        elif isinstance(operand, DateTime):
            dt = operand.get_datetime()

            if p.to_datetime_index() > operand.get_precision().to_datetime_index():
                return None

            if p == Precision.YEAR:
                return dt.year
            elif p == Precision.MONTH:
                return dt.month
            elif p == Precision.DAY:
                return dt.day
            elif p == Precision.HOUR:
                return dt.hour
            elif p == Precision.MINUTE:
                return dt.minute
            elif p == Precision.SECOND:
                return dt.second
            elif p == Precision.MILLISECOND:
                return dt.microsecond // 1000

        elif isinstance(operand, Time):
            time_obj = operand.get_time()

            if p.to_time_index() > operand.get_precision().to_time_index():
                return None

            if p == Precision.HOUR:
                return time_obj.hour
            elif p == Precision.MINUTE:
                return time_obj.minute
            elif p == Precision.SECOND:
                return time_obj.second
            elif p == Precision.MILLISECOND:
                return time_obj.microsecond // 1000

        raise InvalidOperatorArgument(
            "_precision_ from(Date), _precision_ from(DateTime) or _precision_ from(Time)",
            f"{precision.lower()}_from({type(operand).__name__})"
        )


class TimezoneOffsetFromEvaluator(TemporalEvaluator):
    """
    Extracts the timezone offset from a DateTime value.
    """

    def __init__(self, operand_expr):
        self.operand_expr = operand_expr

    def evaluate(self, context: Context) -> Optional[Decimal]:
        operand = self.operand_expr.evaluate(context)
        return self.timezone_offset_from(operand)

    @staticmethod
    def timezone_offset_from(operand: Any) -> Optional[Decimal]:
        """Extract timezone offset from operand."""
        if operand is None:
            return None

        if isinstance(operand, DateTime):
            offset = operand.get_datetime().utcoffset()
            if offset:
                return Decimal(offset.total_seconds() / 3600)
            return None

        raise InvalidOperatorArgument(
            "timezoneoffset_from(DateTime)",
            f"timezoneoffset_from({type(operand).__name__})"
        )


class DurationBetweenEvaluator(TemporalEvaluator):
    """
    Returns the number of whole calendar periods between two temporal values.
    """

    def __init__(self, left_expr, right_expr, precision_str: str):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[int]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.duration(left, right, Precision.from_string(self.precision_str))

    @staticmethod
    def duration(left: Any, right: Any, precision: Precision) -> Optional[int]:
        """Calculate duration between two temporal values."""
        if left is None or right is None:
            return None

        if isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            is_weeks = precision == Precision.WEEK
            if is_weeks:
                precision = Precision.DAY

            # Handle uncertain values
            left_uncertain = left.is_uncertain(precision)
            right_uncertain = right.is_uncertain(precision)

            if left_uncertain and right_uncertain:
                return None

            if left_uncertain:
                interval = left.get_uncertainty_interval(precision)
                high = DurationBetweenEvaluator.duration(
                    interval.get_end(), right,
                    Precision.WEEK if is_weeks else precision
                )
                low = DurationBetweenEvaluator.duration(
                    interval.get_start(), right,
                    Precision.WEEK if is_weeks else precision
                )
                return Interval(high, True, low, True).set_uncertain(True)

            if right_uncertain:
                interval = right.get_uncertainty_interval(precision)
                low = DurationBetweenEvaluator.duration(
                    left, interval.get_start(),
                    Precision.WEEK if is_weeks else precision
                )
                high = DurationBetweenEvaluator.duration(
                    left, interval.get_end(),
                    Precision.WEEK if is_weeks else precision
                )
                return Interval(low, True, high, True).set_uncertain(True)

            # Calculate duration
            if isinstance(left, DateTime) and isinstance(right, DateTime):
                left_dt = left.get_datetime()
                right_dt = right.get_datetime()

                if precision.to_datetime_index() <= Precision.DAY.to_datetime_index():
                    delta = right_dt.date() - left_dt.date()
                else:
                    delta = right_dt - left_dt

                days = delta.days if hasattr(delta, 'days') else int(delta.total_seconds() / 86400)

                if is_weeks:
                    return days // 7
                elif precision == Precision.DAY:
                    return days
                elif precision == Precision.MONTH:
                    return (right_dt.year - left_dt.year) * 12 + (right_dt.month - left_dt.month)
                elif precision == Precision.YEAR:
                    return right_dt.year - left_dt.year

            elif isinstance(left, Date) and isinstance(right, Date):
                left_date = left.get_date()
                right_date = right.get_date()
                delta = right_date - left_date
                days = delta.days

                if is_weeks:
                    return days // 7
                elif precision == Precision.DAY:
                    return days
                elif precision == Precision.MONTH:
                    return (right_date.year - left_date.year) * 12 + (right_date.month - left_date.month)
                elif precision == Precision.YEAR:
                    return right_date.year - left_date.year

            elif isinstance(left, Time) and isinstance(right, Time):
                left_time = left.get_time()
                right_time = right.get_time()
                delta = datetime.combine(date.today(), right_time) - datetime.combine(date.today(), left_time)

                if precision == Precision.HOUR:
                    return int(delta.total_seconds() // 3600)
                elif precision == Precision.MINUTE:
                    return int(delta.total_seconds() // 60)
                elif precision == Precision.SECOND:
                    return int(delta.total_seconds())
                elif precision == Precision.MILLISECOND:
                    return int(delta.total_seconds() * 1000)

        raise InvalidOperatorArgument(
            "duration_between(Date, Date), duration_between(DateTime, DateTime), duration_between(Time, Time)",
            f"duration_between({type(left).__name__}, {type(right).__name__})"
        )


class DifferenceBetweenEvaluator(TemporalEvaluator):
    """
    Returns the number of boundaries crossed for a specified precision between two temporal values.
    """

    def __init__(self, left_expr, right_expr, precision_str: str):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[int]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.difference(left, right, Precision.from_string(self.precision_str))

    @staticmethod
    def difference(left: Any, right: Any, precision: Precision) -> Optional[int]:
        """Calculate difference between two temporal values."""
        if left is None or right is None:
            return None

        if isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            is_weeks = precision == Precision.WEEK
            if is_weeks:
                precision = Precision.DAY

            # Handle uncertain values
            left_uncertain = left.is_uncertain(precision)
            right_uncertain = right.is_uncertain(precision)

            if left_uncertain and right_uncertain:
                return None

            if left_uncertain:
                interval = left.get_uncertainty_interval(precision)
                high = DifferenceBetweenEvaluator.difference(
                    interval.get_end(), right,
                    Precision.WEEK if is_weeks else precision
                )
                low = DifferenceBetweenEvaluator.difference(
                    interval.get_start(), right,
                    Precision.WEEK if is_weeks else precision
                )
                return Interval(high, True, low, True).set_uncertain(True)

            if right_uncertain:
                interval = right.get_uncertainty_interval(precision)
                low = DifferenceBetweenEvaluator.difference(
                    left, interval.get_start(),
                    Precision.WEEK if is_weeks else precision
                )
                high = DifferenceBetweenEvaluator.difference(
                    left, interval.get_end(),
                    Precision.WEEK if is_weeks else precision
                )
                return Interval(low, True, high, True).set_uncertain(True)

            # Calculate difference (truncate to precision)
            if isinstance(left, DateTime) and isinstance(right, DateTime):
                left_dt = left.expand_partial_min_from_precision(precision).get_datetime()
                right_dt = right.expand_partial_min_from_precision(precision).get_datetime()

                if precision.to_datetime_index() <= Precision.DAY.to_datetime_index():
                    delta = right_dt.date() - left_dt.date()
                else:
                    delta = right_dt - left_dt

                days = delta.days if hasattr(delta, 'days') else int(delta.total_seconds() / 86400)

                if is_weeks:
                    return days // 7
                elif precision == Precision.DAY:
                    return days
                elif precision == Precision.MONTH:
                    return (right_dt.year - left_dt.year) * 12 + (right_dt.month - left_dt.month)
                elif precision == Precision.YEAR:
                    return right_dt.year - left_dt.year

            elif isinstance(left, Date) and isinstance(right, Date):
                left_date = left.expand_partial_min_from_precision(precision).get_date()
                right_date = right.expand_partial_min_from_precision(precision).get_date()
                delta = right_date - left_date
                days = delta.days

                if is_weeks:
                    return days // 7
                elif precision == Precision.DAY:
                    return days
                elif precision == Precision.MONTH:
                    return (right_date.year - left_date.year) * 12 + (right_date.month - left_date.month)
                elif precision == Precision.YEAR:
                    return right_date.year - left_date.year

            elif isinstance(left, Time) and isinstance(right, Time):
                left_time = left.expand_partial_min_from_precision(precision).get_time()
                right_time = right.expand_partial_min_from_precision(precision).get_time()
                delta = datetime.combine(date.today(), right_time) - datetime.combine(date.today(), left_time)

                if precision == Precision.HOUR:
                    return int(delta.total_seconds() // 3600)
                elif precision == Precision.MINUTE:
                    return int(delta.total_seconds() // 60)
                elif precision == Precision.SECOND:
                    return int(delta.total_seconds())
                elif precision == Precision.MILLISECOND:
                    return int(delta.total_seconds() * 1000)

        raise InvalidOperatorArgument(
            "difference_between(Date, Date), difference_between(DateTime, DateTime), difference_between(Time, Time)",
            f"difference_between({type(left).__name__}, {type(right).__name__})"
        )


class BeforeEvaluator(TemporalEvaluator):
    """
    Compares temporal values or intervals to determine if one is before another.
    Supports both interval and temporal overloads.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.before(left, right, self.precision_str, context)

    @staticmethod
    def before(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Compare if left is before right."""
        if left is None or right is None:
            return None

        # Interval, Interval
        if isinstance(left, Interval) and isinstance(right, Interval):
            return BeforeEvaluator.before(left.get_end(), right.get_start(), precision, context)

        # Interval, Point
        elif isinstance(left, Interval):
            return BeforeEvaluator.before(left.get_end(), right, precision, context)

        # Point, Interval
        elif isinstance(right, Interval):
            return BeforeEvaluator.before(left, right.get_start(), precision, context)

        # Temporal comparisons
        elif isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            if precision is None:
                precision = BaseTemporal.get_highest_precision(left, right)

            result = left.compare_to_precision(right, Precision.from_string(precision))
            return None if result is None else result < 0

        # Fallback to less comparison for non-temporal types
        from cql_engine.elm.evaluators.comparison import LessEvaluator
        return LessEvaluator.less(left, right, context)


class AfterEvaluator(TemporalEvaluator):
    """
    Compares temporal values or intervals to determine if one is after another.
    Supports both interval and temporal overloads.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.after(left, right, self.precision_str, context)

    @staticmethod
    def after(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Compare if left is after right."""
        if left is None or right is None:
            return None

        # Interval, Interval
        if isinstance(left, Interval) and isinstance(right, Interval):
            return AfterEvaluator.after(left.get_start(), right.get_end(), precision, context)

        # Interval, Point
        elif isinstance(left, Interval):
            return AfterEvaluator.after(left.get_start(), right, precision, context)

        # Point, Interval
        elif isinstance(right, Interval):
            return AfterEvaluator.after(left, right.get_end(), precision, context)

        # Temporal comparisons
        elif isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            if precision is None:
                precision = BaseTemporal.get_highest_precision(left, right)

            result = left.compare_to_precision(right, Precision.from_string(precision))
            return None if result is None else result > 0

        # Fallback to greater comparison for non-temporal types
        from cql_engine.elm.evaluators.comparison import GreaterEvaluator
        return GreaterEvaluator.greater(left, right, context)


class SameAsEvaluator(TemporalEvaluator):
    """
    Compares temporal values or intervals for equality at a specified precision.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.same_as(left, right, self.precision_str, context)

    @staticmethod
    def same_as(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Compare if left is same as right."""
        if left is None or right is None:
            return None

        # Interval, Interval
        if isinstance(left, Interval) and isinstance(right, Interval):
            left_start = left.get_start()
            left_end = left.get_end()
            right_start = right.get_start()
            right_end = right.get_end()

            if all(isinstance(x, BaseTemporal) for x in [left_start, left_end, right_start, right_end]):
                if precision is None:
                    start_precision = BaseTemporal.get_highest_precision(left_start, right_start)
                    precision = BaseTemporal.get_highest_precision(left_end, right_end)
                else:
                    start_precision = precision

                start_result = left_start.compare_to_precision(
                    right_start, Precision.from_string(start_precision)
                )
                end_result = left_end.compare_to_precision(
                    right_end, Precision.from_string(precision)
                )

                if start_result is None and end_result is None:
                    return None
                elif start_result is None and end_result != 0:
                    return False
                elif end_result is None and start_result != 0:
                    return False

                return (start_result is None or end_result is None) or (start_result == 0 and end_result == 0)

        # Temporal comparisons
        elif isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            if precision is None:
                precision = BaseTemporal.get_highest_precision(left, right)

            result = left.compare_to_precision(right, Precision.from_string(precision))
            return None if result is None else result == 0

        raise InvalidOperatorArgument(
            "same_as(Date, Date), same_as(DateTime, DateTime), same_as(Time, Time) or same_as(Interval<T>, Interval<T>)",
            f"same_as({type(left).__name__}, {type(right).__name__})"
        )


class SameOrBeforeEvaluator(TemporalEvaluator):
    """
    Compares temporal values or intervals to determine if one is same as or before another.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.same_or_before(left, right, self.precision_str, context)

    @staticmethod
    def same_or_before(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Compare if left is same as or before right."""
        if left is None or right is None:
            return None

        # Interval overloads
        if isinstance(left, Interval) or isinstance(right, Interval):
            return SameOrBeforeEvaluator.on_or_before(left, right, precision, context)

        # Temporal comparisons
        if precision is None and isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            precision = BaseTemporal.get_highest_precision(left, right)

        if isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            result = left.compare_to_precision(right, Precision.from_string(precision))
            return None if result is None else (result == 0 or result < 0)

        raise InvalidOperatorArgument(
            "same_or_before(Date, Date), same_or_before(DateTime, DateTime), same_or_before(Time, Time)",
            f"same_or_before({type(left).__name__}, {type(right).__name__})"
        )

    @staticmethod
    def on_or_before(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Interval overload for on or before."""
        # Interval, Interval
        if isinstance(left, Interval) and isinstance(right, Interval):
            if isinstance(left.get_start(), BaseTemporal):
                return SameOrBeforeEvaluator.same_or_before(
                    left.get_end(), right.get_start(), precision, context
                )
            from cql_engine.elm.evaluators.comparison import LessOrEqualEvaluator
            return LessOrEqualEvaluator.less_or_equal(left.get_end(), right.get_start(), context)

        # Interval, Point
        elif isinstance(left, Interval):
            if isinstance(right, BaseTemporal):
                return SameOrBeforeEvaluator.same_or_before(left.get_end(), right, precision, context)
            from cql_engine.elm.evaluators.comparison import LessOrEqualEvaluator
            return LessOrEqualEvaluator.less_or_equal(left.get_end(), right, context)

        # Point, Interval
        elif isinstance(right, Interval):
            if isinstance(left, BaseTemporal):
                return SameOrBeforeEvaluator.same_or_before(left, right.get_start(), precision, context)
            from cql_engine.elm.evaluators.comparison import LessOrEqualEvaluator
            return LessOrEqualEvaluator.less_or_equal(left, right.get_start(), context)

        raise InvalidOperatorArgument(
            "on_or_before(Date, Date), on_or_before(DateTime, DateTime), on_or_before(Time, Time)",
            f"on_or_before({type(left).__name__}, {type(right).__name__})"
        )


class SameOrAfterEvaluator(TemporalEvaluator):
    """
    Compares temporal values or intervals to determine if one is same as or after another.
    """

    def __init__(self, left_expr, right_expr, precision_str: Optional[str] = None):
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.precision_str = precision_str

    def evaluate(self, context: Context) -> Optional[bool]:
        left = self.left_expr.evaluate(context)
        right = self.right_expr.evaluate(context)
        return self.same_or_after(left, right, self.precision_str, context)

    @staticmethod
    def same_or_after(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Compare if left is same as or after right."""
        if left is None or right is None:
            return None

        # Interval overloads
        if isinstance(left, Interval) or isinstance(right, Interval):
            return SameOrAfterEvaluator.on_or_after(left, right, precision, context)

        # Temporal comparisons
        if precision is None and isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            precision = BaseTemporal.get_highest_precision(left, right)

        if isinstance(left, BaseTemporal) and isinstance(right, BaseTemporal):
            result = left.compare_to_precision(right, Precision.from_string(precision))
            return None if result is None else (result == 0 or result > 0)

        raise InvalidOperatorArgument(
            "same_or_after(Date, Date), same_or_after(DateTime, DateTime), same_or_after(Time, Time)",
            f"same_or_after({type(left).__name__}, {type(right).__name__})"
        )

    @staticmethod
    def on_or_after(left: Any, right: Any, precision: Optional[str], context: Context) -> Optional[bool]:
        """Interval overload for on or after."""
        # Interval, Interval
        if isinstance(left, Interval) and isinstance(right, Interval):
            if isinstance(left.get_start(), BaseTemporal):
                return SameOrAfterEvaluator.same_or_after(
                    left.get_start(), right.get_end(), precision, context
                )
            from cql_engine.elm.evaluators.comparison import GreaterOrEqualEvaluator
            return GreaterOrEqualEvaluator.greater_or_equal(left.get_start(), right.get_end(), context)

        # Interval, Point
        elif isinstance(left, Interval):
            if isinstance(right, BaseTemporal):
                return SameOrAfterEvaluator.same_or_after(left.get_start(), right, precision, context)
            from cql_engine.elm.evaluators.comparison import GreaterOrEqualEvaluator
            return GreaterOrEqualEvaluator.greater_or_equal(left.get_start(), right, context)

        # Point, Interval
        elif isinstance(right, Interval):
            if isinstance(left, BaseTemporal):
                return SameOrAfterEvaluator.same_or_after(left, right.get_end(), precision, context)
            from cql_engine.elm.evaluators.comparison import GreaterOrEqualEvaluator
            return GreaterOrEqualEvaluator.greater_or_equal(left, right.get_end(), context)

        raise InvalidOperatorArgument(
            "on_or_after(Date, Date), on_or_after(DateTime, DateTime), on_or_after(Time, Time)",
            f"on_or_after({type(left).__name__}, {type(right).__name__})"
        )
