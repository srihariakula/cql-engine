"""DSTU3-specific FHIR type converter."""

from .dstu2_type_converter import Dstu2FhirTypeConverter


class Dstu3FhirTypeConverter(Dstu2FhirTypeConverter):
    """FHIR type converter for DSTU3 (HL7 FHIR version 3.0.1).

    Inherits from DSTU2 with version-specific customizations as needed.
    """

    pass
