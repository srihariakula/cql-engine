"""
Clinical/terminology evaluators for CQL expressions.

Handles value set references, code system references, retrieve operations, etc.
"""

from abc import ABC
from typing import Any, Optional, List
from datetime import datetime, date

from cql_engine.execution.context import Context
from cql_engine.execution.exceptions import InvalidOperatorArgument
from cql_engine.runtime.cql_code import Code, Concept


class ClinicalEvaluator(ABC):
    """Base class for clinical evaluators."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the clinical operation."""
        raise NotImplementedError


class RetrieveEvaluator(ClinicalEvaluator):
    """
    Retrieves resources from a data provider based on a data type and optional criteria.
    """

    def __init__(self, data_type: str, code_path: Optional[str] = None, codes_expr=None,
                 date_range_expr=None):
        self.data_type = data_type
        self.code_path = code_path
        self.codes_expr = codes_expr
        self.date_range_expr = date_range_expr

    def evaluate(self, context: Context) -> Optional[List[Any]]:
        """Retrieve resources."""
        # Evaluate codes if provided
        codes = None
        if self.codes_expr:
            codes = self.codes_expr.evaluate(context)

        # Evaluate date range if provided
        date_range = None
        if self.date_range_expr:
            date_range = self.date_range_expr.evaluate(context)

        # Call data provider
        return context.retrieve(
            self.data_type,
            code_path=self.code_path,
            codes=codes,
            date_range=date_range
        )


class CodeSystemRefEvaluator(ClinicalEvaluator):
    """
    References a code system by name/URI.
    """

    def __init__(self, code_system_name: str):
        self.code_system_name = code_system_name

    def evaluate(self, context: Context) -> Any:
        """Resolve code system reference."""
        return context.resolve_code_system_ref(self.code_system_name)


class ValueSetRefEvaluator(ClinicalEvaluator):
    """
    References a value set by name/URI.
    """

    def __init__(self, value_set_name: str):
        self.value_set_name = value_set_name

    def evaluate(self, context: Context) -> Any:
        """Resolve value set reference."""
        return context.resolve_value_set_ref(self.value_set_name)


class CodeRefEvaluator(ClinicalEvaluator):
    """
    Creates a code reference.
    """

    def __init__(self, code: str, code_system: str, version: Optional[str] = None,
                 display: Optional[str] = None):
        self.code = code
        self.code_system = code_system
        self.version = version
        self.display = display

    def evaluate(self, context: Context) -> Code:
        """Create code reference."""
        return Code(
            code=self.code,
            system=self.code_system,
            version=self.version,
            display=self.display
        )


class ConceptRefEvaluator(ClinicalEvaluator):
    """
    Creates a concept reference.
    """

    def __init__(self, codes: List[Code], display: Optional[str] = None):
        self.codes = codes
        self.display = display

    def evaluate(self, context: Context) -> Concept:
        """Create concept reference."""
        return Concept(codes=self.codes, display=self.display)


class InValueSetEvaluator(ClinicalEvaluator):
    """
    Returns true if a code is in a value set.
    """

    def __init__(self, code_expr, value_set_expr):
        self.code_expr = code_expr
        self.value_set_expr = value_set_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        """Check if code is in value set."""
        code = self.code_expr.evaluate(context)
        value_set = self.value_set_expr.evaluate(context)

        if code is None or value_set is None:
            return None

        return self.in_value_set(code, value_set, context)

    @staticmethod
    def in_value_set(code: Any, value_set: Any, context: Context) -> Optional[bool]:
        """Check membership in value set."""
        # Call value set provider
        return context.code_in_value_set(code, value_set)


class InCodeSystemEvaluator(ClinicalEvaluator):
    """
    Returns true if a code is in a code system.
    """

    def __init__(self, code_expr, code_system_expr):
        self.code_expr = code_expr
        self.code_system_expr = code_system_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        """Check if code is in code system."""
        code = self.code_expr.evaluate(context)
        code_system = self.code_system_expr.evaluate(context)

        if code is None or code_system is None:
            return None

        return self.in_code_system(code, code_system, context)

    @staticmethod
    def in_code_system(code: Any, code_system: Any, context: Context) -> Optional[bool]:
        """Check membership in code system."""
        # Call code system provider
        return context.code_in_code_system(code, code_system)


class AnyInValueSetEvaluator(ClinicalEvaluator):
    """
    Returns true if any code in a list is in a value set.
    """

    def __init__(self, codes_expr, value_set_expr):
        self.codes_expr = codes_expr
        self.value_set_expr = value_set_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        """Check if any code is in value set."""
        codes = self.codes_expr.evaluate(context)
        value_set = self.value_set_expr.evaluate(context)

        if codes is None or value_set is None:
            return None

        if not isinstance(codes, (list, tuple)):
            codes = [codes]

        for code in codes:
            if InValueSetEvaluator.in_value_set(code, value_set, context):
                return True

        return False


class AnyInCodeSystemEvaluator(ClinicalEvaluator):
    """
    Returns true if any code in a list is in a code system.
    """

    def __init__(self, codes_expr, code_system_expr):
        self.codes_expr = codes_expr
        self.code_system_expr = code_system_expr

    def evaluate(self, context: Context) -> Optional[bool]:
        """Check if any code is in code system."""
        codes = self.codes_expr.evaluate(context)
        code_system = self.code_system_expr.evaluate(context)

        if codes is None or code_system is None:
            return None

        if not isinstance(codes, (list, tuple)):
            codes = [codes]

        for code in codes:
            if InCodeSystemEvaluator.in_code_system(code, code_system, context):
                return True

        return False


class ExpandValueSetEvaluator(ClinicalEvaluator):
    """
    Expands a value set and returns all codes in it.
    """

    def __init__(self, value_set_expr):
        self.value_set_expr = value_set_expr

    def evaluate(self, context: Context) -> Optional[List[Code]]:
        """Expand value set."""
        value_set = self.value_set_expr.evaluate(context)

        if value_set is None:
            return None

        # Call value set provider to expand
        return context.expand_value_set(value_set)


class CalculateAgeEvaluator(ClinicalEvaluator):
    """
    Calculates age based on birth date (from birthDate to evaluation date).
    """

    def __init__(self, birth_date_expr):
        self.birth_date_expr = birth_date_expr

    def evaluate(self, context: Context) -> Optional[int]:
        """Calculate age."""
        birth_date = self.birth_date_expr.evaluate(context)

        if birth_date is None:
            return None

        return self.calculate_age(birth_date, context)

    @staticmethod
    def calculate_age(birth_date: Any, context: Context) -> Optional[int]:
        """Calculate age from birth date."""
        eval_date = context.get_evaluation_datetime()

        if isinstance(birth_date, str):
            try:
                birth_date = datetime.fromisoformat(birth_date)
            except (ValueError, TypeError):
                return None

        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()

        if isinstance(eval_date, datetime):
            eval_date = eval_date.date()

        if not isinstance(birth_date, date) or not isinstance(eval_date, date):
            return None

        # Calculate age
        age = eval_date.year - birth_date.year
        if (eval_date.month, eval_date.day) < (birth_date.month, birth_date.day):
            age -= 1

        return age


class CalculateAgeAtEvaluator(ClinicalEvaluator):
    """
    Calculates age at a specific date (from birthDate to specified date).
    """

    def __init__(self, birth_date_expr, date_expr):
        self.birth_date_expr = birth_date_expr
        self.date_expr = date_expr

    def evaluate(self, context: Context) -> Optional[int]:
        """Calculate age at specific date."""
        birth_date = self.birth_date_expr.evaluate(context)
        at_date = self.date_expr.evaluate(context)

        if birth_date is None or at_date is None:
            return None

        return self.calculate_age_at(birth_date, at_date)

    @staticmethod
    def calculate_age_at(birth_date: Any, at_date: Any) -> Optional[int]:
        """Calculate age at specific date."""
        if isinstance(birth_date, str):
            try:
                birth_date = datetime.fromisoformat(birth_date)
            except (ValueError, TypeError):
                return None

        if isinstance(at_date, str):
            try:
                at_date = datetime.fromisoformat(at_date)
            except (ValueError, TypeError):
                return None

        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()

        if isinstance(at_date, datetime):
            at_date = at_date.date()

        if not isinstance(birth_date, date) or not isinstance(at_date, date):
            return None

        # Calculate age
        age = at_date.year - birth_date.year
        if (at_date.month, at_date.day) < (birth_date.month, birth_date.day):
            age -= 1

        return age
