"""R5-specific FHIR type converter."""

from .dstu2_type_converter import Dstu2FhirTypeConverter


class R5FhirTypeConverter(Dstu2FhirTypeConverter):
    """FHIR type converter for R5 (HL7 FHIR version 5.0.0).

    Inherits from DSTU2 with R5-specific customizations as needed.
    """

    pass
