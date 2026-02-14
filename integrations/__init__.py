"""
EHR/EMR Integration Module
Supports HL7 v2.x and FHIR R4 standards for hospital system integration
"""

from .hl7_integration import HL7Integration
from .fhir_integration import FHIRIntegration
from .ehr_adapter import EHRAdapter

__all__ = ['HL7Integration', 'FHIRIntegration', 'EHRAdapter']
