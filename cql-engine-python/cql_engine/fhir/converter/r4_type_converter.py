"""R4-specific FHIR type converter."""

from .dstu2_type_converter import Dstu2FhirTypeConverter


class R4FhirTypeConverter(Dstu2FhirTypeConverter):
    """FHIR type converter for R4 (HL7 FHIR version 4.0.1).

    Inherits from DSTU2 with R4-specific customizations as needed.
    """

    pass
