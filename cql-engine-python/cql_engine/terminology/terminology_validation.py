"""
Terminology validation for CQL engine.

Maintains known code systems and provides validation of terminology systems.
"""

from typing import Set, List


class TerminologyValidation:
    """
    Provides validation and management of known coding systems.

    Maintains a static set of known standard medical and healthcare coding systems.
    """

    # Standard medical and healthcare coding systems
    SYSTEMS: Set[str] = {
        "http://snomed.info/sct",
        "http://loinc.org",
        "http://unitsofmeasure.org",
        "http://www.nlm.nih.gov/research/umls/rxnorm",
        "http://ncimeta.nci.nih.gov",
        "http://www.ama-assn.org/go/cpt",
        "http://hl7.org/fhir/ndfrt",
        "http://fdasis.nlm.nih.gov",
        "http://hl7.org/fhir/sid/ndc",
        "http://hl7.org/fhir/sid/cvx",
        "http://www.nubc.org/patient-discharge",
        "http://www.radlex.org",
        "http://hl7.org/fhir/sid/icd-10",
        "http://hl7.org/fhir/sid/icd-10-de",
        "http://hl7.org/fhir/sid/icd-10-nl",
        "http://hl7.org/fhir/sid/icd-10-us",
        "http://www.icd10data.com/icd10pcs",
        "http://hl7.org/fhir/sid/icd-9-cm",
        "http://hl7.org/fhir/sid/icd-9-cm/diagnosis",
        "http://hl7.org/fhir/sid/icd-9-cm/procedure",
        "http://hl7.org/fhir/sid/icpc-1",
        "http://hl7.org/fhir/sid/icpc-1-nl",
        "http://hl7.org/fhir/sid/icpc-2",
        "http://hl7.org/fhir/sid/icf-nl",
        "http://www.whocc.no/atc",
        "http://nema.org/dicom/dicm",
        "http://hl7.org/fhir/sid/ca-hc-din",
        "http://nucc.org/provider-taxonomy",
        "http://www.genenames.org",
        "http://www.ensembl.org",
        "http://www.ncbi.nlm.nih.gov/nuccore",
        "http://www.ncbi.nlm.nih.gov/clinvar",
        "http://sequenceontology.org",
        "http://www.hgvs.org/mutnomen",
        "http://www.ncbi.nlm.nih.gov/projects/SNP",
        "http://cancer.sanger.ac.uk/cancergenome/projects/cosmic",
        "http://www.lrg-sequence.org",
        "http://www.omim.org",
        "http://www.ncbi.nlm.nih.gov/pubmed",
        "http://www.pharmgkb.org",
        "http://clinicaltrials.gov",
        "http://www.ebi.ac.uk/ipd/imgt/hla/",
    }

    def __init__(self):
        """Private constructor - this class provides only static methods."""
        pass

    @staticmethod
    def add_system(system: str) -> None:
        """
        Add a coding system to the known systems set.

        Args:
            system: The system URI to add
        """
        TerminologyValidation.SYSTEMS.add(system)

    @staticmethod
    def get_systems() -> Set[str]:
        """
        Get the set of known coding systems.

        Returns:
            Set of system URIs
        """
        return TerminologyValidation.SYSTEMS

    @staticmethod
    def set_systems(new_systems: List[str]) -> None:
        """
        Replace the entire set of known systems.

        Args:
            new_systems: List of system URIs to set as the known systems
        """
        TerminologyValidation.SYSTEMS = set(new_systems)

    @staticmethod
    def has_system(system: str) -> bool:
        """
        Check if a system is in the known systems set.

        Args:
            system: The system URI to check

        Returns:
            True if the system is known, False otherwise
        """
        return system in TerminologyValidation.SYSTEMS
