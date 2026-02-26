"""FHIR-specific exceptions."""

from .unknown_element import UnknownElement
from .unknown_path import UnknownPath
from .unknown_type import UnknownType
from .version_mismatch import FhirVersionMismatchException

__all__ = [
    "UnknownElement",
    "UnknownPath",
    "UnknownType",
    "FhirVersionMismatchException",
]
